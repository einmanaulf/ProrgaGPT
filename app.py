from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, date
from alembic import op
import sqlalchemy as sa
from waitress import serve


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prorga.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importer les modèles pour éviter les erreurs de référence circulaire
import models

# Importer les routes après l'initialisation de db
import routes



def get_funds():
    funds = db.session.query(Funds).first()
    return funds.amount if funds else 1000

def update_funds_in_db(funds):
    funds_record = db.session.query(Funds).first()
    if funds_record:
        funds_record.amount = funds
    else:
        new_funds = Funds(amount=funds)
        db.session.add(new_funds)
    db.session.commit()

# Révision ID utilisée par Alembic.
revision = 'ajoutez_votre_revision_id_ici'
down_revision = 'revision_id_precedente_ici'
branch_labels = None
depends_on = None

def upgrade():
    # Ajout des colonnes à la table task
    op.add_column('task', sa.Column('time_required', sa.Float(), nullable=True))
    op.add_column('task', sa.Column('time_unit', sa.String(length=20), nullable=True))

def downgrade():
    # Suppression des colonnes ajoutées
    op.drop_column('task', 'time_required')
    op.drop_column('task', 'time_unit')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

