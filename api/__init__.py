from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, static_folder="statics")
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    db.init_app(app)
    CORS(app)

    from .user import user
    # from .project import project
    # from .task import task

    app.register_blueprint(user)
    # app.register_blueprint(project)
    # app.register_blueprint(task)
    
    @app.route('/welcome')
    def home():
        return "<h1>Hello everyone, welcome to the next big thing</h1>"

    return app

    