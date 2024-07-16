from test_config import get_db
from test_models import Task

# Créer une session
db = next(get_db())

# Ajouter des tâches avec des relations de prérequis
task1 = Task(name="Task 1")
task2 = Task(name="Task 2")
task3 = Task(name="Task 3")

task2.prerequisites.append(task1)
task3.prerequisites.append(task2)

db.add(task1)
db.add(task2)
db.add(task3)
db.commit()

# Récupérer les tâches et afficher leurs prérequis
tasks = db.query(Task).all()
for task in tasks:
    print(f"{task.name} prerequisites: {[prereq.name for prereq in task.prerequisites]}")
