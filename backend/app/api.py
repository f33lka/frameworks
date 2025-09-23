import io
import logging
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd
from flask import Blueprint, abort, current_app, jsonify, request, send_file
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import and_, func, or_
from werkzeug.security import safe_str_cmp
from wtforms import Form, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, ValidationError

from app import bcrypt, db
from app.models import (Attachment, Comment, Defect, History, PriorityEnum,
                        Project, RoleEnum, Stage, StatusEnum, User)

# ------------------------ настройки ------------------------
api_bp = Blueprint('api', __name__)
csrf = CSRFProtect()
LOG = logging.getLogger(__name__)

ACCESS_EXPIRES = timedelta(hours=2)

# ------------------------ вспомогательные декораторы ------------------------
def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            ident = get_jwt_identity()          # {'id': 1, 'role': 'manager'}
            if ident['role'] not in roles:
                LOG.warning('Access denied for user %s (role %s) to %s', ident['id'], ident['role'], request.endpoint)
                return jsonify(msg='Недостаточно прав'), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# ------------------------ WTForms-валидация ------------------------
class LoginForm(Form):
    email    = StringField(validators=[InputRequired()])
    password = StringField(validators=[InputRequired()])

class RegisterForm(Form):
    email     = StringField(validators=[InputRequired()])
    password  = StringField(validators=[InputRequired()])
    full_name = StringField(validators=[InputRequired()])
    role      = SelectField(choices=[(r, r) for r in RoleEnum], validators=[InputRequired()])

class DefectCreateForm(Form):
    title       = StringField(validators=[InputRequired()])
    description = StringField(validators=[InputRequired()])
    priority    = SelectField(choices=[(p, p) for p in PriorityEnum], validators=[InputRequired()])
    project_id  = IntegerField(validators=[InputRequired()])
    stage_id    = IntegerField()   # опционально
    assigned_to = IntegerField()   # опционально
    due_date    = StringField()    # придёт строка ISO

# ------------------------ AUTH ------------------------
@api_bp.post('/register')
def register():
    form = RegisterForm(request.form)
    if not form.validate():
        return jsonify(errors=form.errors), 400
    if User.query.filter_by(email=form.email.data).first():
        return jsonify(msg='Email уже занят'), 409
    u = User(
        email=form.email.data,
        full_name=form.full_name.data,
        role=RoleEnum(form.role.data),
    )
    u.password = form.password.data
    db.session.add(u)
    db.session.commit()
    LOG.info('New user %s', u.id)
    return jsonify(id=u.id, email=u.email), 201

@api_bp.post('/login')
def login():
    form = LoginForm(request.form)
    if not form.validate():
        return jsonify(errors=form.errors), 400
    u = User.query.filter_by(email=form.email.data).first()
    if not u or not u.verify_password(form.password.data):
        return jsonify(msg='Неверные данные'), 401
    token = create_access_token(identity={'id': u.id, 'role': u.role}, expires_delta=ACCESS_EXPIRES)
    LOG.info('Login user %s', u.id)
    return jsonify(access_token=token, user={'id': u.id, 'email': u.email, 'full_name': u.full_name, 'role': u.role})

@api_bp.get('/me')
@jwt_required()
def me():
    ident = get_jwt_identity()
    u = User.query.get(ident['id'])
    return jsonify(id=u.id, email=u.email, full_name=u.full_name, role=u.role)

# ------------------------ PROJECTS ------------------------
@api_bp.get('/projects')
@jwt_required()
def list_projects():
    # пока все проекты видят все
    rows = Project.query.filter(Project.deleted_at.is_(None)).all()
    return jsonify([{'id': p.id, 'name': p.name, 'address': p.address} for p in rows])

@api_bp.post('/projects')
@role_required(RoleEnum.MANAGER)
def create_project():
    data = request.get_json()
    p = Project(name=data['name'], address=data.get('address'), description=data.get('description'))
    db.session.add(p)
    db.session.commit()
    return jsonify(id=p.id), 201

# ------------------------ STAGES ------------------------
@api_bp.get('/projects/<int:pid>/stages')
@jwt_required()
def list_stages(pid):
    rows = Stage.query.filter_by(project_id=pid).order_by(Stage.order_index).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in rows])

# ------------------------ DEFECTS ------------------------
@api_bp.get('/defects')
@jwt_required()
def list_defects():
    # фильтры приходят в query-string: ?status=new&priority=high&project_id=1
    ident = get_jwt_identity()
    role = ident['role']
    q = Defect.query.filter(Defect.deleted_at.is_(None))

    if role == RoleEnum.ENGINEER:
        # инженер видит только свои и те, где он исполнитель
        q = q.filter(or_(Defect.created_by == ident['id'], Defect.assigned_to == ident['id']))
    # manager/observer видят всё

    status = request.args.get('status')
    priority = request.args.get('priority')
    project_id = request.args.get('project_id', type=int)
    if status:   q = q.filter(Defect.status == StatusEnum(status))
    if priority: q = q.filter(Defect.priority == PriorityEnum(priority))
    if project_id: q = q.filter(Defect.project_id == project_id)

    rows = q.order_by(Defect.created_at.desc()).all()
    return jsonify([
        {
            'id': d.id,
            'title': d.title,
            'description': d.description,
            'status': d.status.value,
            'priority': d.priority.value,
            'due_date': d.due_date.isoformat() if d.due_date else None,
            'project': {'id': d.project.id, 'name': d.project.name},
            'stage': {'id': d.stage.id, 'name': d.stage.name} if d.stage else None,
            'creator': {'id': d.creator.id, 'full_name': d.creator.full_name},
            'assignee': {'id': d.assignee.id, 'full_name': d.assignee.full_name} if d.assignee else None,
        } for d in rows
    ])

@api_bp.post('/defects')
@jwt_required()
def create_defect():
    ident = get_jwt_identity()
    data = request.get_json()
    form = DefectCreateForm(data=data)
    if not form.validate():
        return jsonify(errors=form.errors), 400
    d = Defect(
        title=data['title'],
        description=data['description'],
        priority=PriorityEnum(data['priority']),
        project_id=data['project_id'],
        stage_id=data.get('stage_id'),
        assigned_to=data.get('assigned_to'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        created_by=ident['id'],
    )
    db.session.add(d)
    db.session.commit()
    LOG.info('Defect %s created by user %s', d.id, ident['id'])
    return jsonify(id=d.id), 201

@api_bp.put('/defects/<int:did>')
@jwt_required()
def update_defect(did):
    ident = get_jwt_identity()
    d = Defect.query.get_or_404(did)
    data = request.get_json()

    # проверяем права
    if ident['role'] == RoleEnum.ENGINEER and d.created_by != ident['id'] and d.assigned_to != ident['id']:
        return jsonify(msg='Можно редактировать только свои дефекты'), 403
    if ident['role'] == RoleEnum.OBSERVER:
        return jsonify(msg='Недостаточно прав'), 403

    # пишем историю
    for field in ('title', 'description', 'status', 'priority', 'assigned_to', 'due_date'):
        if field in data:
            old = getattr(d, field)
            new = data[field]
            if field == 'status': new = StatusEnum(new)
            if field == 'priority': new = PriorityEnum(new)
            if old != new:
                db.session.add(History(defect_id=did, user_id=ident['id'], field_name=field, old_value=str(old), new_value=str(new)))
                setattr(d, field, new)
    d.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(msg='Обновлено')

@api_bp.delete('/defects/<int:did>')
@jwt_required()
def delete_defect(did):
    ident = get_jwt_identity()
    d = Defect.query.get_or_404(did)
    if ident['role'] != RoleEnum.MANAGER:
        return jsonify(msg='Удалять может только менеджер'), 403
    d.deleted_at = datetime.utcnow()
    db.session.commit()
    return '', 204

# ------------------------ COMMENTS ------------------------
@api_bp.post('/defects/<int:did>/comments')
@jwt_required()
def add_comment(did):
    ident = get_jwt_identity()
    body = request.get_json()['body']
    c = Comment(defect_id=did, author_id=ident['id'], body=body)
    db.session.add(c)
    db.session.commit()
    return jsonify(id=c.id), 201

@api_bp.get('/defects/<int:did>/comments')
@jwt_required()
def list_comments(did):
    rows = Comment.query.filter_by(defect_id=did).order_by(Comment.created_at).all()
    return jsonify([
        {'id': c.id, 'body': c.body, 'created_at': c.created_at.isoformat(),
         'author': {'id': c.author.id, 'full_name': c.author.full_name}} for c in rows
    ])

# ------------------------ ATTACHMENTS ------------------------
@api_bp.post('/defects/<int:did>/attachments')
@jwt_required()
def upload_attachment(did):
    if 'file' not in request.files:
        return jsonify(msg='Файл не найден'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(msg='Файл не выбран'), 400
    # сохраняем
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{did}_{ts}_{file.filename}"
    path = current_app.config['ATTACHMENT_FOLDER'] / filename
    file.save(path)
    att = Attachment(defect_id=did, filename=file.filename, stored_path=str(path),
                     file_size=file.content_length or 0, mime_type=file.mimetype)
    db.session.add(att)
    db.session.commit()
    return jsonify(id=att.id), 201

# ------------------------ REPORTS / EXPORT ------------------------
@api_bp.get('/reports/export')
@role_required(RoleEnum.MANAGER)
def export_report():
    fmt = request.args.get('format', 'xlsx')  # xlsx или csv
    q = Defect.query.filter(Defect.deleted_at.is_(None))
    df = pd.read_sql(q.statement, db.session.bind)
    # убираем лишние колонки
    df = df[['id', 'title', 'description', 'status', 'priority', 'due_date', 'project_id', 'assigned_to']]
    buf = io.BytesIO()
    if fmt == 'csv':
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, mimetype='text/csv', download_name=f'defects_{datetime.now():%Y%m%d}.csv', as_attachment=True)
    else:
        df.to_excel(buf, index=False)
        buf.seek(0)
        return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         download_name=f'defects_{datetime.now():%Y%m%d}.xlsx', as_attachment=True)

# ------------------------ ANALYTICS ------------------------
@api_bp.get('/reports/stats')
@jwt_required()
def stats():
    # простая статистика по статусам и приоритетам
    status_counts = db.session.query(Defect.status, func.count(Defect.id)).group_by(Defect.status).all()
    priority_counts = db.session.query(Defect.priority, func.count(Defect.id)).group_by(Defect.priority).all()
    return jsonify(
        status={s.value: c for s, c in status_counts},
        priority={p.value: c for p, c in priority_counts},
    )