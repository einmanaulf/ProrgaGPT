from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db  # Assurez-vous que app et db sont importés correctement

migrate = Migrate(app, db)
manager = Manager(app)

# Ajout de la commande db pour les migrations
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
