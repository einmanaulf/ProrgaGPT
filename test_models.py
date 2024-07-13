from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    prerequisite = db.relationship('Task', remote_side=[id], backref='dependent_tasks')


with app.app_context():
    db.create_all()

    task1 = Task(name="Task 1")
    task2 = Task(name="Task 2", prerequisite=task1)

    db.session.add(task1)
    db.session.add(task2)
    db.session.commit()

    tasks = Task.query.all()
    for task in tasks:
        print(task.name, task.prerequisite.name if task.prerequisite else "No prerequisite")
