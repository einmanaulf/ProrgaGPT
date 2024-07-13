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

# Assurez-vous que les modèles sont importés
import models  # Importer tous les modèles ici

if __name__ == "__main__":
    from routes import *  # Importer les routes ici pour éviter les importations circulaires
    app.run(host="0.0.0.0", port=80, debug=True)
