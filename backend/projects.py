from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import db
from models import Project
from utils import role_required

bp = Blueprint("projects", __name__, url_prefix="/api/projects")

@bp.get("")
@jwt_required()
def list_projects():
    items = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description} for p in items])

@bp.post("")
@role_required("manager")
def create_project():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    if Project.query.filter_by(name=name).first():
        return jsonify({"error": "project exists"}), 409
    p = Project(name=name, description=data.get("description", ""))
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id, "name": p.name, "description": p.description}), 201

@bp.put("/<int:pid>")
@role_required("manager")
def update_project(pid):
    p = Project.query.get_or_404(pid)
    data = request.get_json() or {}
    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return jsonify({"error": "name required"}), 400
        p.name = name
    if "description" in data:
        p.description = data["description"] or ""
    db.session.commit()
    return jsonify({"id": p.id, "name": p.name, "description": p.description})

@bp.delete("/<int:pid>")
@role_required("manager")
def delete_project(pid):
    p = Project.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})
