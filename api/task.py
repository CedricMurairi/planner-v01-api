from flask import Blueprint, request, current_app, abort
from .models import Task, TaskLabel, Label
import datetime
from . import db
from .user import admin_auth_required, auth_required


task = Blueprint("task", __name__)

@task.route('/tasks', methods=['POST'])
@auth_required
def create_task(u=None):
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
    project = request.json.get('project')
    vals = request.json.get('due').split("-")
    due = datetime.datetime(int(vals[0]), int(vals[1]), int(vals[2]))
    labels = request.json.get('labels')
    task = Task(name=name, description=description, user_id=creator, project_id=project, due=due)
    db.session.add(task)
    db.session.commit()

    if labels and len(labels) > 0:
        for label in labels:
            if Label.query.get(label) and not TaskLabel(task_id=task.id, label_id=label):
                task_label = TaskLabel(task_id=task.id, label_id=label)
                db.session.add(task_label)
                db.session.commit()

    return {
        "message": "Task created successfully",
        "data": {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "creator": {
                "id": task.creator.id,
                "name": task.creator.name,
                "email": task.creator.email,
                "username": task.creator.username,
                "avatar": task.creator.avatar,
                "profile": task.creator.profile
            },
            "project": {
                "id": task.project.id,
                "name": task.project.name,
                "description": task.project.description,
                "ends": task.project.ends
            },
            "due": task.due,
            "completed": task.completed,
            "labels": [
                {
                    "id": label.label.id,
                    "name": label.label.name,
                    "color": label.label.name
                } for label in task.labels
            ]
        }
    }, 200

@task.route('/tasks/<int:id>', methods=['GET'])
@auth_required
def get_task(id, u=None):
    task = Task.query.filter_by(id=id, user_id=u.id).first()
    if not task:
        abort(404)

    return {
        "message": "Task retrieved successfully",
        "data": {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "creator": {
                "id": task.creator.id,
                "name": task.creator.name,
                "email": task.creator.email,
                "username": task.creator.username,
                "avatar": task.creator.avatar,
                "profile": task.creator.profile
            },
            "project": {
                "id": task.project.id,
                "name": task.project.name,
                "description": task.project.description,
                "ends": task.project.ends
            },
            "due": task.due,
            "completed": task.completed,
            "labels": [
                {
                    "id": label.label.id,
                    "name": label.label.name,
                    "color": label.label.name
                } for label in task.labels
            ] 
        }
    }, 200

@task.route('/tasks/all', methods=['GET'])
@auth_required 
def get_tasks(u=None):
    tasks = Task.query.filter_by(user_id=u.id).all()
    if len(tasks) > 0:
        return {
            "message": "Tasks retrieved successfully",
            "data": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "creator": {
                        "id": task.creator.id,
                        "name": task.creator.name,
                        "email": task.creator.email,
                        "username": task.creator.username,
                        "avatar": task.creator.avatar,
                        "profile": task.creator.profile
                    },
                    "project": {
                        "id": task.project.id,
                        "name": task.project.name,
                        "description": task.project.description,
                        "ends": task.project.ends
                    },
                    "due": task.due,
                    "completed": task.completed,
                    "labels": [
                        {
                            "id": label.label.id,
                            "name": label.label.name,
                            "color": label.label.name
                        } for label in task.labels
                    ]
                } for task in tasks
            ]
        }, 200

    abort(404)

@task.route('/tasks/<int:id>', methods=['DELETE'])
@auth_required 
def delete_task(id, u=None):
    task = Task.query.filter_by(id=id, user_id=u.id).first()

    if task:
        db.session.delete(task)
        db.session.commit()

        return {
            "message": "Tasks deleted successfully"
        }, 200

    return {
        "message": "Task not found"
    }, 404

@task.route('/tasks/<int:id>', methods=['PUT'])
@auth_required 
def uptade_task(id, u=None):
    if not request.json:
        abort(400)

    task = Task.query.filter_by(id=id, user_id=u.id).first()
    if task:
        task.name = request.json.get("name") or task.name
        task.description = request.json.get("description") or task.description
        vals = request.json.get('due').split("-")
        due = datetime.datetime(int(vals[0]), int(vals[1]), int(vals[2]))
        task.due = due or task.due
        task.completed = request.json.get("completed") or task.completed

        db.session.add(task)
        db.session.commit()

        return {
            "message": "Tasks updated successfully",
            "data":{
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "creator": {
                    "id": task.creator.id,
                    "name": task.creator.name,
                    "email": task.creator.email,
                    "username": task.creator.username,
                    "avatar": task.creator.avatar,
                    "profile": task.creator.profile
                },
                "project": {
                    "id": task.project.id,
                    "name": task.project.name,
                    "description": task.project.description,
                    "ends": task.project.ends
                },
                "due": task.due,
                "completed": task.completed,
                "labels": [
                    {
                        "id": label.label.id,
                        "name": label.label.name,
                        "color": label.label.name
                    } for label in task.labels
                ]
            }
        }, 200

    return {
        "message": "Task not found"
    }, 404

@task.route('/tasks/<int:id>/labels', methods=['DELETE'])
@auth_required
def delete_task_label(id, u=None):
    task = Task.query.get(id)
    if not task.user_id == u.id:
        abort(401)

    if not request.json:
        abort(400)

    t_label = TaskLabel.query.filter_by(label_id=request.json.get('label'), task_id=id).first()
    if not t_label:
        abort(404)
    db.session.delete(t_label)
    db.session.commit()

    return {
        "message": "Label was deleted successfully"
    }, 200

@task.route('/tasks/<int:id>/labels', methods=['POST'])
@auth_required
def add_task_label(id, u=None):
    task = Task.query.get(id)
    if not task.user_id == u.id:
        abort(401)

    if not request.json:
        abort(400)

    labels = request.json.get('labels')
    if labels and len(labels) > 0:
        for label in labels:
            if Label.query.get(label) and not TaskLabel.query.filter_by(label_id=label, task_id=id).first():
                t_label = TaskLabel(task_id=id, label_id=label)
                db.session.add(t_label)
                db.session.commit()
        return {
            "message": "Label was created successfully"
        }, 200

    abort(400)