from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging

# Configurez le logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("Lancement de l'application")

app = Flask(__name__)

# Configuration de la base de données avec un chemin absolu
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "instance", "prorga.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    from models import *  # Importez tous les modèles après avoir configuré db et migrate
    from routes import *  # Assurez-vous que les routes sont importées correctement ici
    app.run(host="127.0.0.1", port=5000, debug=True)
