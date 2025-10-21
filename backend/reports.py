from flask import Blueprint, jsonify
from sqlalchemy import func
from flask_jwt_extended import jwt_required
from database import db
from models import Defect

bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@bp.get("/summary")
@jwt_required()
def summary():
    total = db.session.scalar(db.select(func.count()).select_from(Defect)) or 0
    by_status = dict(db.session.execute(db.select(Defect.status, func.count()).group_by(Defect.status)).all())
    by_priority = dict(db.session.execute(db.select(Defect.priority, func.count()).group_by(Defect.priority)).all())
    return jsonify({"total": total, "by_status": by_status, "by_priority": by_priority})
