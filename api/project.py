from flask import Blueprint, request, current_app, abort
from .models import Project, ProjectLabel, Label
import datetime
from . import db
from .user import admin_auth_required, auth_required


project = Blueprint("project", __name__)

@project.route('/projects', methods=['POST'])
@auth_required
def create_project(u=None):
    if not request.json:
        abort(400)

    user_id = request.json.get('creator')
    if user_id != u.id:
        return {
            "message": "No read or write access to endpoint"
        }, 403
    
    name = request.json.get('name')
    description = request.json.get('description')
    creator = request.json.get('creator') 
    vals = request.json.get('ends').split("-")
    ends = datetime.datetime(int(vals[0]), int(vals[1]), int(vals[2]))
    labels = request.json.get('labels')
    project = Project(name=name, description=description, user_id=creator, ends=ends)
    db.session.add(project)
    db.session.commit()

    if labels and len(labels) > 0:
        for label in labels:
            if Label.query.get(label) and not ProjectLabel(project_id=project.id, label_id=label):
                project_label = ProjectLabel(project_id=project.id, label_id=label)
                db.session.add(project_label)
                db.session.commit()

    return {
        "message": "Project created successfully",
        "data": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "creator": {
                "id": project.manager.id,
                "name": project.manager.name,
                "email": project.manager.email,
                "username": project.manager.username,
                "avatar": project.manager.avatar,
                "profile": project.manager.profile
            },
            "created": project.created,
            "ends": project.ends,
            "completed": project.completed,
            "tasks": [task for task in project.tasks],
            "labels": [label for label in project.labels]
        }
    }

@project.route('/projects/<int:id>', methods=['GET'])
@auth_required
def get_project(id, u=None):
    project = Project.query.filter_by(id=id, user_id=u.id).first()
    if not project:
        abort(404)

    return {
        "message": "Project retrieved successfully",
        "data": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "creator": {
                "id": project.manager.id,
                "name": project.manager.name,
                "email": project.manager.email,
                "username": project.manager.username,
                "avatar": project.manager.avatar,
                "profile": project.manager.profile,
            },
            "created": project.created,
            "ends": project.ends,
            "completed": project.completed,
            "tasks": [task for task in project.tasks],
            "labels": [label for label in project.labels] 
        }
    }, 200

@project.route('/projects/all', methods=['GET'])
@auth_required 
def get_projects(u=None):
    projects = Project.query.filter_by(user_id=u.id).all()
    if len(projects) > 0:
        return {
            "message": "Projects retrieved successfully",
            "data": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "creator": {
                        "id": project.manager.id,
                        "name": project.manager.name,
                        "email": project.manager.email,
                        "username": project.manager.username,
                        "avatar": project.manager.avatar,
                        "profile": project.manager.profile
                    },
                    "ends": project.ends,
                    "completed": project.completed,
                    "tasks": [task for task in project.tasks],
                    "labels": [label for label in project.labels]
                } for project in projects
            ]
        }, 200

    abort(404)

@project.route('/projects/<int:id>', methods=['DELETE'])
@auth_required 
def delete_project(id, u=None):
    project = Project.query.filter_by(id=id, user_id=u.id).first()

    if project:
        db.session.delete(project)
        db.session.commit()

        return {
            "message": "Projects deleted successfully"
        }, 200

    return {
        "message": "Project not found"
    }, 404

@project.route('/projects/<int:id>', methods=['PUT'])
@auth_required 
def uptade_project(id, u=None):
    if not request.json:
        abort(400)

    project = Project.query.filter_by(id=id, user_id=u.id).first()
    project.name = request.json.get("name") or project.name
    project.description = request.json.get("description") or project.description
    vals = request.json.get('ends').split("-")
    ends = datetime.datetime(int(vals[0]), int(vals[1]), int(vals[2]))
    project.ends = ends or project.ends
    project.completed = request.json.get("completed") or project.completed

    db.session.add(project)
    db.session.commit()

    if project:
        return {
            "message": "Projects updated successfully",
            "data":{
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "creator": {
                    "id": project.manager.id,
                    "name": project.manager.name,
                    "email": project.manager.email,
                    "username": project.manager.username,
                    "avatar": project.manager.avatar,
                    "profile": project.manager.profile
                },
                "ends": project.ends,
                "completed": project.completed,
                "tasks": [task for task in project.tasks],
                "labels": [label for label in project.labels]
            }
        }, 200

    return {
        "message": "Project not found"
    }, 404

@project.route('/projects/<int:id>/labels', methods=['DELETE'])
@auth_required
def delete_project_label(id, u=None):
    project = Project.query.get(id)
    if not project.user_id == u.id:
        abort(401)

    if not request.json:
        abort(400)

    p_label = ProjectLabel.query.filter_by(label_id=request.json.get('label'), project_id=id).first()
    if not p_label:
        abort(404)
    db.session.delete(p_label)
    db.session.commit()

    return {
        "message": "Label was deleted successfully"
    }, 200


