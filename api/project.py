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

