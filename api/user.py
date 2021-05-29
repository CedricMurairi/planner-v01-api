from flask import Blueprint, request, abort, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from functools import wraps
from .models import User
from . import db
from sqlalchemy import or_

user = Blueprint('user', __name__)

def auth_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if not 'Authorization' in request.headers:
            return {
                "message": "Did not find any Token"
            }, 401
        try:
            s = Serializer(current_app.config['SECRET_KEY'])
            raw_token = request.headers['Authorization']
            token = str.replace(str(raw_token), 'Bearer ', '')
            data = s.loads(token)
            user = User.query.filter_by(id=data.get('id'), email=data.get('email')).first()
            if not user:
                return {
                    "message": "Couldn't get data from Token, either corrupt or expired"
                }, 401

        except Exception as e:
            return {
                "message": e.__str__()
            }, 401

        return view(u=user, *args, **kwargs)

    return decorated_function

def admin_auth_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if not 'Authorization' in request.headers:
            return {
                "message": "Did not find any Token"
            }, 401
        try:
            s = Serializer(current_app.config['SECRET_KEY'])
            raw_token = request.headers['Authorization']
            token = str.replace(str(raw_token), 'Bearer ', '')
            data = s.loads(token)
            user = User.query.filter_by(id=data.get('id'), email=data.get('email')).first()
            if not user and not user.is_admin:
                return {
                    "message": "Either token is corrupt or you're not authorized to access"
                }, 401

        except Exception as e:
            return {
                "message": e.__str__()
            }, 401

        return view(u=user, *args, **kwargs)

    return decorated_function


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
            "is_admin": user.is_admin,
            "activated": user.activated,
            "suspended": user.suspended,
            "avatar": user.avatar,
            "profile": user.profile
        }
    }, 200

@user.route('/users/all', methods=['GET'])
@admin_auth_required
def get_users(u=None):
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
@auth_required
def get_user(id, u=None):
    user = User.query.get(id)
    if user.id != u.id and not u.is_admin:
        return {
            "message": "No read or write access to endpoint"
        }, 403

    if user:
        return {
            "message": "Retrieved successful",
            "data": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
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
@auth_required
def delete_user(id, u=None):
    user = User.query.get(id)
    if user.id != u.id and not user.is_admin:
        return {
            "message": "No read or write access to endpoint"
        }, 403

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
@auth_required
def update(id, u=None):
    user = User.query.get(id)
    if user.id != u.id and not user.is_admin:
        return {
            "message": "No read or write access to endpoint"
        }, 403

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