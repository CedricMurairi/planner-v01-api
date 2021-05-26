from flask import request, current_app
import hashlib
from datetime import datetime
from api import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json

# class MyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if hasattr(obj, '__json__'):
#             return obj.__json__()
#         return json.JSONEncoder.default(self, obj)

class User(db.Model):

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar is None:
            self.avatar = self.generate_avatar()

        if self.email == current_app.config['APP_ADMIN']:
            self.is_admin = True

    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pass_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(128), nullable=False)
    profile = db.Column(db.String(128), default=None)
    is_admin = db.Column(db.Boolean, default=False)
    activated = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)
    projects = db.relationship('Project', backref='manager', lazy='dynamic', cascade="all, delete")
    tasks  = db.relationship('Task', backref='creator', lazy='dynamic', cascade="all, delete")
    labels = db.relationship('Label', backref='owner', lazy='dynamic', cascade="all, delete")

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pass_hash, password)

    def generate_avatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_auth_token(self, expiration=2592000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id, 'email': self.email})

    def verify_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('id') != self.id or data.get('email') != self.email:
            return False
        return True

    def generate_verification_token(self, expiration=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id, 'email': self.email})

    def activate(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('id') != self.id or data.get('email') != self.email:
            return False
        self.activated = True
        db.session.add(self)
        db.session.commit()
        return True

class Project(db.Model):

    __tablename__="projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    use_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, default=datetime.now())
    ends = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade="all, delete")
    labels = db.relationship('ProjectLabel', backref='projects', lazy='dynamic', cascade="all, delete")

class Task(db.Model):

    __tablename__="tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    labels = db.relationship('TaskLabel', backref='tasks', lazy='dynamic', cascade="all, delete")

class Label(db.Model):

    __tablename__="labels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_labels = db.relationship('ProjectLabel', backref='label', lazy='dynamic', cascade="all, delete")
    task_labels = db.relationship('TaskLabel', backref='label', lazy='dynamic', cascade="all, delete")

class ProjectLabel(db.Model):

    __tablename__="projectlabels"
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)

class TaskLabel(db.Model):

    __tablename__="tasklabels"
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), primary_key=True)
    label_id = db.Column(db.Integer, db.ForeignKey('labels.id'), primary_key=True)
