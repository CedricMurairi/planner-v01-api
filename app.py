import os
from api import create_app, db
from flask_script import Manager, Shell
from api.models import User, Project, Task, Label, TaskLabel, ProjectLabel
from flask_migrate import Migrate


app = create_app(os.getenv('FLASK_ENV') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

@manager.command
def create_table():
	"""Create tables"""
	db.create_all()
	print('Tables created')

def make_shell_context():
	return dict(app=app, db=db, User=User, Project=Project, Task=Task, Label=Label, TaskLabel=TaskLabel, ProjectLabel=ProjectLabel)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    with app.app_context():
        manager.run()
        app.run()