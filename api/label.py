from flask import Blueprint, request, current_app, abort
from .models import Label
import datetime
from . import db
from .user import admin_auth_required, auth_required


label = Blueprint("label", __name__)

@label.route('/labels', methods=['POST'])
@auth_required
def create_label(u=None):
    if not request.json:
        abort(400)

    user_id = request.json.get('owner')
    if user_id != u.id:
        return {
            "message": "No read or write access to endpoint"
        }, 403
    
    name = request.json.get('name')
    color = request.json.get('color')
    user_id = request.json.get('owner')
    label = Label(name=name, user_id=user_id, color=color)
    db.session.add(label)
    db.session.commit()

    return {
        "message": "Label created successfully",
        "data": {
            "id": label.id,
            "name": label.name,
            "color": label.color,
        }
    }, 200

@label.route('/labels/<int:id>', methods=['GET'])
@auth_required
def get_label(id, u=None):
    label = Label.query.filter_by(id=id, user_id=u.id).first()
    if not label:
        abort(404)

    return {
        "message": "Label retrieved successfully",
        "data": {
            "id": label.id,
            "name": label.name,
            "color": label.color,
        }
    }, 200

@label.route('/labels/all', methods=['GET'])
@auth_required 
def get_labels(u=None):
    labels = Label.query.filter_by(user_id=u.id).all()
    if len(labels) > 0:
        return {
            "message": "Labels retrieved successfully",
            "data": [
                {
                    "id": label.id,
                    "name": label.name,
                    "color": label.color,
                } for label in labels
            ]
        }, 200

    abort(404)

