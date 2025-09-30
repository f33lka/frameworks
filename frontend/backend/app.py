import os
from datetime import date, datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'habits.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    goal_per_week = db.Column(db.Integer, default=5)

class Checkin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    day = db.Column(db.Date, default=date.today)
    habit = db.relationship('Habit')

def init_db():
    db.create_all()
    if Habit.query.count() == 0:
        h1 = Habit(title='Тренировка', goal_per_week=3)
        h2 = Habit(title='Английский', goal_per_week=5)
        db.session.add_all([h1, h2]); db.session.commit()

@app.route('/api/health')
def health():
    return {'status':'ok'}

@app.route('/api/habits', methods=['GET','POST','PATCH'])
def habits():
    if request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        goal = int(data.get('goal_per_week', 5))
        if not title: return jsonify({'error':'title_required'}), 400
        h = Habit(title=title, goal_per_week=goal)
        db.session.add(h); db.session.commit()
        return jsonify({'id':h.id}), 201
    if request.method == 'PATCH':
        data = request.get_json() or {}
        h = Habit.query.get(data.get('id'))
        if not h: return jsonify({'error':'not_found'}), 404
        for f in ['title','goal_per_week']:
            if f in data: setattr(h, f, data[f])
        db.session.commit()
        return jsonify({'ok':True})
    items = Habit.query.order_by(Habit.id.desc()).all()
    return jsonify([{'id':h.id,'title':h.title,'goal_per_week':h.goal_per_week} for h in items])

@app.route('/api/checkins', methods=['GET','POST','DELETE'])
def checkins():
    if request.method == 'POST':
        data = request.get_json() or {}
        habit_id = data.get('habit_id')
        dstr = (data.get('day') or '').strip()
        d = date.today()
        if dstr:
            try:
                d = datetime.strptime(dstr, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error':'bad_date_format','need':'YYYY-MM-DD'}), 400
        if not Habit.query.get(habit_id): return jsonify({'error':'habit_not_found'}), 404
        # prevent duplicates same day
        exist = Checkin.query.filter_by(habit_id=habit_id, day=d).first()
        if exist: return jsonify({'id': exist.id}), 200
        ch = Checkin(habit_id=habit_id, day=d); db.session.add(ch); db.session.commit()
        return jsonify({'id': ch.id}), 201
    if request.method == 'DELETE':
        hid = request.args.get('id', type=int)
        ch = Checkin.query.get(hid)
        if not ch: return jsonify({'error':'not_found'}), 404
        db.session.delete(ch); db.session.commit()
        return jsonify({'ok':True})
    # GET last 30 days
    since = date.today() - timedelta(days=29)
    items = Checkin.query.filter(Checkin.day >= since).order_by(Checkin.day.desc()).all()
    return jsonify([{'id':c.id,'habit_id':c.habit_id,'habit':c.habit.title if c.habit else None,'day':c.day.isoformat()} for c in items])

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
