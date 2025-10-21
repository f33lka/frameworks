from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from database import db
from models import Defect, Project, User
from utils import role_required

bp = Blueprint("defects", __name__, url_prefix="/api/defects")

ALLOWED_STATUSES = {"new","in_progress","in_review","closed","cancelled"}
ALLOWED_PRIORITIES = {"low","medium","high"}

@bp.get("")
@jwt_required()
def list_defects():
    q = Defect.query
    project_id = request.args.get("project_id", type=int)
    status = request.args.get("status")
    priority = request.args.get("priority")
    assignee_id = request.args.get("assignee_id", type=int)
    search = request.args.get("q","").strip()

    if project_id:
        q = q.filter(Defect.project_id==project_id)
    if status:
        q = q.filter(Defect.status==status)
    if priority:
        q = q.filter(Defect.priority==priority)
    if assignee_id:
        q = q.filter(Defect.assignee_id==assignee_id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Defect.title.ilike(like), Defect.description.ilike(like)))

    items = q.order_by(Defect.created_at.desc()).all()
    return jsonify([serialize_defect(d) for d in items])

@bp.post("")
@jwt_required()
def create_defect():
    data = request.get_json() or {}
    project_id = data.get("project_id")
    title = (data.get("title") or "").strip()
    if not project_id or not title:
        return jsonify({"error":"project_id and title required"}), 400
    if not Project.query.get(project_id):
        return jsonify({"error":"project not found"}), 404
    priority = (data.get("priority") or "medium").lower()
    if priority not in ALLOWED_PRIORITIES:
        return jsonify({"error":"invalid priority"}), 400
    d = Defect(
        project_id=project_id,
        title=title,
        description=data.get("description",""),
        priority=priority,
        status="new",
        assignee_id=data.get("assignee_id")
    )
    db.session.add(d)
    db.session.commit()
    return jsonify(serialize_defect(d)), 201

@bp.patch("/<int:did>/status")
@jwt_required()
def update_status(did):
    d = Defect.query.get_or_404(did)
    data = request.get_json() or {}
    new_status = (data.get("status") or "").lower()
    if new_status not in ALLOWED_STATUSES:
        return jsonify({"error":"invalid status"}), 400
    allowed = {
        "new": {"in_progress","cancelled"},
        "in_progress": {"in_review","cancelled"},
        "in_review": {"closed","in_progress","cancelled"},
        "closed": set(),
        "cancelled": set()
    }
    if new_status not in allowed.get(d.status, set()):
        return jsonify({"error":"invalid transition", "from": d.status, "to": new_status}), 409
    d.status = new_status
    db.session.commit()
    return jsonify(serialize_defect(d))

@bp.put("/<int:did>")
@jwt_required()
def update_defect(did):
    d = Defect.query.get_or_404(did)
    data = request.get_json() or {}
    if "title" in data:
        t = (data["title"] or "").strip()
        if not t:
            return jsonify({"error":"title required"}), 400
        d.title = t
    if "description" in data:
        d.description = data["description"] or ""
    if "priority" in data:
        pr = (data["priority"] or "").lower()
        if pr not in ALLOWED_PRIORITIES:
            return jsonify({"error":"invalid priority"}), 400
        d.priority = pr
    if "assignee_id" in data:
        aid = data["assignee_id"]
        if aid and not User.query.get(aid):
            return jsonify({"error":"assignee not found"}), 404
        d.assignee_id = aid
    db.session.commit()
    return jsonify(serialize_defect(d))

@bp.delete("/<int:did>")
@role_required("manager")
def delete_defect(did):
    d = Defect.query.get_or_404(did)
    db.session.delete(d)
    db.session.commit()
    return jsonify({"ok": True})

def serialize_defect(d: Defect):
    return {
        "id": d.id,
        "project_id": d.project_id,
        "title": d.title,
        "description": d.description,
        "priority": d.priority,
        "status": d.status,
        "assignee_id": d.assignee_id,
        "created_at": d.created_at.isoformat(),
        "updated_at": d.updated_at.isoformat() if d.updated_at else None
    }
