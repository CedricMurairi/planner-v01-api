from flask import Blueprint, request, abort
from .models import User
from . import db
from sqlalchemy import or_

user = Blueprint('user', __name__)

@user.route('/login', methods=['POST'])
def login():
    if not request.authorization:
        abort(400)

    email = request.authorization.username
    password = request.authorization.password
    
    user = User.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        token = user.generate_auth_token()
        return {
            "message": "Login success",
            "data": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "tasks": [task for task in user.tasks],
                "projects": [project for project in user.projects],
                "labels": [label for label in user.labels],
                "is_admin": user.is_admin,
                "activated": user.activated,
                "suspended": user.suspended,
                "avatar": user.avatar,
                "profile": user.profile,
                "auth_token": token.decode()
            }
        }, 200

    return {
        "error": "Bad request",
        "message": "Incorrect email or password"
    }, 400

@user.route('/register', methods=['POST'])
def register():
    if not request.json:
        abort(400)

    email = request.json['email']
    username = request.json['username']
    name = request.json['name']
    password = request.json['password']

    check = User.query.filter(or_(User.email==email, User.username==username)).all()
    if len(check) > 0:
        return {
            "error": "Bad request",
            "message": "Email or username already in use"
        }, 400

    user = User(name=name, email=email, username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return {
        "message": "Registration success",
        "data": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "tasks": [task for task in user.tasks],
            "projects": [project for project in user.projects],
            "labels": [label for label in user.labels],
            "is_admin": user.is_admin,
            "activated": user.activated,
            "suspended": user.suspended,
            "avatar": user.avatar,
            "profile": user.profile
        }
    }, 200

@user.route('/users/all', methods=['GET'])
def get_users():
    users = User.query.all()
    if len(users) > 0:
        return {
            "message": "Retrieved successful",
            "data":[
                {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "email": user.email,
                    "tasks": [task for task in user.tasks],
                    "projects": [project for project in user.projects],
                    "labels": [label for label in user.labels],
                    "is_admin": user.is_admin,
                    "activated": user.activated,
                    "suspended": user.suspended,
                    "avatar": user.avatar,
                    "profile": user.profile  
                } for user in users
            ]
        }, 200

    return {
        "message": "No users found"
    }, 404

@user.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return {
            "message": "Retrieved successful",
            "data": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "tasks": [task for task in user.tasks],
                "projects": [project for project in user.projects],
                "labels": [label for label in user.labels],
                "is_admin": user.is_admin,
                "activated": user.activated,
                "suspended": user.suspended,
                "avatar": user.avatar,
                "profile": user.profile
            }
        }, 200
    return {
        "message": "User not found"
    }, 404

@user.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {
            "message": "User deleted successfully"
        }, 200

    return {
        "message": "Unser not fount"
    }, 404

@user.route('/users/<int:id>', methods=['PUT'])
def update(id):
    user = User.query.get(id)
    if user:
        email = request.json['email'] or user.email
        name = request.json['name'] or user.name
        username = request.json['username'] or user.username
        check = User.query.filter(or_(User.email, User.username)).first()
        if check:
            return {
                "message": "Email or Username already in use"
            }, 400
        user.email = email
        user.name = name
        user.username = username
        db.session.add(user)
        db.session.commit()

        return {
            "message": "User updated successfully",
            "data": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "tasks": [task for task in user.tasks],
                "projects": [project for project in user.projects],
                "labels": [label for label in user.labels],
                "is_admin": user.is_admin,
                "activated": user.activated,
                "suspended": user.suspended,
                "avatar": user.avatar,
                "profile": user.profile
            }
        }, 200
    return {
        "message": "User not found"
    }, 404