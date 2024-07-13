import logging
from app import app, db
from models import Task

logging.basicConfig(level=logging.DEBUG)

# Configurer l'application Flask pour le test
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.create_all()

    # Création de tâches et de leurs prérequis
    task1 = Task(name="Task 1")
    task2 = Task(name="Task 2")
    db.session.add(task1)
    db.session.add(task2)
    db.session.commit()

    task2.prerequisites.append(task1)
    db.session.commit()

    # Vérification des relations
    retrieved_task2 = Task.query.filter_by(name="Task 2").first()
    for prerequisite in retrieved_task2.prerequisites:
        print(f'{retrieved_task2.name} has prerequisite: {prerequisite.name}')

print("Test terminé")
