from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, date
from alembic import op
import sqlalchemy as sa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prorga.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Modèles de données

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text, default='')
    principle = db.Column(db.Text, default='')
    protocol = db.Column(db.Text, default='')
    prerequisites = db.Column(db.Text, default='')
    protections = db.Column(db.Text, default='')
    materials = db.Column(db.Text, default='')
    consumables = db.Column(db.Text, default='')
    time_required = db.Column(db.String(50), default='0')
    time_required_unit = db.Column(db.String(20), default='seconds')
    funding = db.Column(db.Float, default=0.0)
    time_to_sell = db.Column(db.String(50), default='0')
    time_to_sell_unit = db.Column(db.String(20), default='seconds')
    tasks = db.relationship('Task', backref='project', lazy=True)

    def calculate_priority(self):
        return (self.urgency + self.impact + self.resources + self.complexity + self.alignment) / 5

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'goal': self.goal,
            'principle': self.principle,
            'protocol': self.protocol,
            'prerequisites': self.prerequisites,
            'protections': self.protections,
            'materials': self.materials,
            'consumables': self.consumables,
            'time_required': self.time_required,
            'time_required_unit': self.time_required_unit,
            'funding': self.funding,
            'time_to_sell': self.time_to_sell,
            'time_to_sell_unit': self.time_to_sell_unit,
            'priority': self.calculate_priority()
        }



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    planned_date = db.Column(db.Date)
    urgency = db.Column(db.Float)
    impact = db.Column(db.Float)
    resources = db.Column(db.Float)
    complexity = db.Column(db.Float)
    alignment = db.Column(db.Float)
    recurrence = db.Column(db.String(100))
    time_required = db.Column(db.Float)
    time_required_unit = db.Column(db.String(20))
    funding = db.Column(db.Float)
    benefits = db.Column(db.Float)
    time_to_sell = db.Column(db.Float)
    time_to_sell_unit = db.Column(db.String(20))
    order = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_name': self.parent_project.name if self.parent_project else None,
            'is_done': self.is_done,
            'due_date': self.due_date,
            'planned_date': self.planned_date,
            'urgency': self.urgency,
            'impact': self.impact,
            'resources': self.resources,
            'complexity': self.complexity,
            'alignment': self.alignment,
            'recurrence': self.recurrence,
            'time_required': self.time_required,
            'time_required_unit': self.time_required_unit,
            'funding': self.funding,
            'benefits': self.benefits,
            'time_to_sell': self.time_to_sell,
            'time_to_sell_unit': self.time_to_sell_unit,
            'order': self.order
        }
class Protection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Consumable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Funds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

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

# Routes

@app.route('/')
def index():
    projects = Project.query.all()
    tasks = Task.query.filter(
        (Task.due_date == date.today()) |
        (Task.planned_date == date.today())
    ).all()
    funds = get_funds()
    return render_template('index.html', projects=projects, tasks=tasks, funds=funds)


@app.route('/update_funds', methods=['POST'])
def update_funds():
    funds = request.form['funds']
    update_funds_in_db(funds)
    return redirect(url_for('index'))

# Routes Tasks

@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            planned_date = request.form.get('planned_date')
            due_date = request.form.get('due_date')
            recurrence = request.form.get('recurrence', '')
            protection_names = request.form.getlist('protections')
            protections = []
            for pname in protection_names:
                protection = Protection.query.filter_by(name=pname).first()
                if not protection:
                    protection = Protection(name=pname, quantity=0)
                    db.session.add(protection)
                protections.append(protection)

            # Traiter les matériels
            material_names = request.form.getlist('materials')
            materials = []
            for mname in material_names:
                material = Material.query.filter_by(name=mname).first()
                if not material:
                    material = Material(name=mname, quantity=0)
                    db.session.add(material)
                materials.append(material)

            # Traiter les consommables
            consumable_names = request.form.getlist('consumables')
            consumables = []
            for cname in consumable_names:
                consumable = Consumable.query.filter_by(name=cname).first()
                if not consumable:
                    consumable = Consumable(name=cname, quantity=0)
                    db.session.add(consumable)
                consumables.append(consumable)

            prerequisites = request.form.get('prerequisites', '')
            time_required = request.form.get('time_required', 0)
            time_unit = request.form.get('time_unit', 'seconds')
            funding = request.form.get('funding', 0)
            benefits = request.form.get('benefits', 0)
            time_to_sell = request.form.get('time_to_sell', 0)
            time_to_sell_unit = request.form.get('time_to_sell_unit', 'seconds')

            new_task = Task(
                name=name,
                planned_date=planned_date,
                due_date=due_date,
                recurrence=recurrence,
                prerequisites=prerequisites,
                protections=protections,
                materials=materials,
                consumables=consumables,
                time_required=time_required,
                time_unit=time_unit,
                funding=funding,
                benefits=benefits,
                time_to_sell=time_to_sell,
                time_to_sell_unit=time_to_sell_unit
            )
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        except KeyError as e:
            return f"Missing data: {str(e)}", 400
    return render_template('tasks/create.html')


@app.route('/tasks/<int:id>/mark_done', methods=['GET'])
def mark_task_done(id):
    task = Task.query.get_or_404(id)
    task.is_done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/create', methods=['POST'])
def create_task_from_home():
    name = request.form['name']
    planned_date = datetime.today().date()
    new_task = Task(
        name=name,
        planned_date=planned_date
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/list')
def list_tasks():
    tasks = Task.query.all()
    return render_template('tasks/list.html', tasks=tasks)


@app.route('/tasks/<int:id>/details')
def task_details(id):
    task = Task.query.get_or_404(id)
    return render_template('tasks/details.html', task=task)

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.planned_date = datetime.strptime(request.form['planned_date'], '%Y-%m-%d').date()
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        task.recurrence = request.form['recurrence']
        task.prerequisites = request.form['prerequisites']
        task.protections = request.form['protections']
        task.materials = request.form['materials']
        task.consumables = request.form['consumables']
        task.time_required = request.form['time_required']
        task.time_unit = request.form['time_unit']
        task.funding = request.form['funding']
        task.benefits = request.form['benefits']
        task.time_to_sell = request.form['time_to_sell']

        db.session.commit()
        return redirect(url_for('list_tasks'))
    return render_template('tasks/edit.html', task=task)

@app.route('/tasks/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('list_tasks'))

@app.route('/tasks/<int:id>/mark_undone', methods=['GET'])
def mark_task_undone(id):
    task = Task.query.get_or_404(id)
    task.is_done = False
    db.session.commit()
    return redirect(url_for('index'))

# Routes Projects

@app.route('/projects/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        goal = request.form.get('goal', '') or ''
        principle = request.form.get('principle', '') or ''
        protocol = request.form.get('protocol', '') or ''
        prerequisites = request.form.get('prerequisites', '') or ''
        protections = request.form.get('protections', '') or ''
        materials = request.form.get('materials', '') or ''
        consumables = request.form.get('consumables', '') or ''
        time_required = request.form.get('time_required', '0') or '0'
        time_required_unit = request.form.get('time_required_unit', 'seconds')
        funding = float(request.form.get('funding', '0') or 0)
        time_to_sell = request.form.get('time_to_sell', '0') or '0'
        time_to_sell_unit = request.form.get('time_to_sell_unit', 'seconds')

        new_project = Project(
            name=name,
            goal=goal,
            principle=principle,
            protocol=protocol,
            prerequisites=prerequisites,
            protections=protections,
            materials=materials,
            consumables=consumables,
            time_required=time_required,
            time_required_unit=time_required_unit,
            funding=funding,
            time_to_sell=time_to_sell,
            time_to_sell_unit=time_to_sell_unit
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('list_projects'))
    return render_template('projects/create.html')


@app.route('/projects/list')
def list_projects():
    projects = Project.query.all()
    return render_template('projects/list.html', projects=projects)


@app.route('/projects/<int:id>/details')
def project_details(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/details.html', project=project)

@app.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.goal = request.form.get('goal', '') or ''
        project.principle = request.form.get('principle', '') or ''
        project.protocol = request.form.get('protocol', '') or ''
        project.prerequisites = request.form.get('prerequisites', '') or ''
        project.protections = request.form.get('protections', '') or ''
        project.materials = request.form.get('materials', '') or ''
        project.consumables = request.form.get('consumables', '') or ''
        project.time_required = request.form.get('time_required', '0') or '0'
        project.time_required_unit = request.form.get('time_required_unit', 'seconds')
        project.funding = float(request.form.get('funding', '0') or 0)
        project.time_to_sell = request.form.get('time_to_sell', '0') or '0'
        project.time_to_sell_unit = request.form.get('time_to_sell_unit', 'seconds')

        db.session.commit()
        return redirect(url_for('list_projects'))
    return render_template('projects/edit.html', project=project)

@app.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('list_projects'))

# Routes materials
@app.route('/materials/create', methods=['GET', 'POST'])
def create_material():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        new_material = Material(name=name, quantity=quantity)
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/create.html')

@app.route('/materials/list')
def list_materials():
    materials = Material.query.all()
    return render_template('materials/list.html', materials=materials)

@app.route('/materials/<int:id>/details')
def material_details(id):
    material = Material.query.get_or_404(id)
    return render_template('materials/details.html', material=material)


@app.route('/materials/<int:id>/edit', methods=['GET', 'POST'])
def edit_material(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        material.name = request.form['name']
        material.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/edit.html', material=material)

@app.route('/materials/<int:id>/delete', methods=['POST'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('list_materials'))

# Routes consumables
@app.route('/consumables/create', methods=['GET', 'POST'])
def create_consumable():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        new_consumable = Consumable(name=name, quantity=quantity)
        db.session.add(new_consumable)
        db.session.commit()
        return redirect(url_for('list_consumables'))
    return render_template('consumables/create.html')

@app.route('/consumables/list')
def list_consumables():
    consumables = Consumable.query.all()
    return render_template('consumables/list.html', consumables=consumables)

@app.route('/consumables/<int:id>/details')
def consumable_details(id):
    consumable = Consumable.query.get_or_404(id)
    return render_template('consumables/details.html', consumable=consumable)

@app.route('/consumables/<int:id>/edit', methods=['GET', 'POST'])
def edit_consumable(id):
    consumable = Consumable.query.get_or_404(id)
    if request.method == 'POST':
        consumable.name = request.form['name']
        consumable.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('list_consumables'))
    return render_template('consumables/edit.html', consumable=consumable)

@app.route('/consumables/<int:id>/delete', methods=['POST'])
def delete_consumable(id):
    consumable = Consumable.query.get_or_404(id)
    db.session.delete(consumable)
    db.session.commit()
    return redirect(url_for('list_consumables'))

# Routes protections
@app.route('/protections/list')
def list_protections():
    protections = Protection.query.all()
    return render_template('protections/list.html', protections=protections)

@app.route('/protections/create', methods=['GET', 'POST'])
def create_protection():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        new_protection = Protection(name=name, quantity=quantity)
        db.session.add(new_protection)
        db.session.commit()
        return redirect(url_for('list_protections'))
    return render_template('protections/create.html')

@app.route('/protections/<int:id>/details')
def protection_details(id):
    protection = Protection.query.get_or_404(id)
    return render_template('protections/details.html', protection=protection)

@app.route('/protections/<int:id>/edit', methods=['GET', 'POST'])
def edit_protection(id):
    protection = Protection.query.get_or_404(id)
    if request.method == 'POST':
        protection.name = request.form['name']
        protection.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('list_protections'))
    return render_template('protections/edit.html', protection=protection)

@app.route('/protections/<int:id>/delete', methods=['POST'])
def delete_protection(id):
    protection = Protection.query.get_or_404(id)
    db.session.delete(protection)
    db.session.commit()
    return redirect(url_for('list_protections'))

#autocomplétions

@app.route('/autocomplete/protections', methods=['GET'])
def autocomplete_protections():
    query = request.args.get('query', '')
    protections = Protection.query.filter(Protection.name.ilike(f'%{query}%')).all()
    results = [{'id': p.id, 'name': p.name} for p in protections]
    return jsonify(results)

@app.route('/autocomplete/materials', methods=['GET'])
def autocomplete_materials():
    query = request.args.get('query', '')
    materials = Material.query.filter(Material.name.ilike(f'%{query}%')).all()
    results = [{'id': m.id, 'name': m.name} for m in materials]
    return jsonify(results)

@app.route('/autocomplete/consumables', methods=['GET'])
def autocomplete_consumables():
    query = request.args.get('query', '')
    consumables = Consumable.query.filter(Consumable.name.ilike(f'%{query}%')).all()
    results = [{'id': c.id, 'name': c.name} for c in consumables]
    return jsonify(results)

@app.route('/autocomplete/prerequisites', methods=['GET'])
def autocomplete_prerequisites():
    query = request.args.get('query', '')
    tasks = Task.query.filter(Task.name.ilike(f'%{query}%')).all()
    projects = Project.query.filter(Project.name.ilike(f'%{query}%')).all()
    results = [{'id': t.id, 'name': t.name, 'type': 'task'} for t in tasks]
    results += [{'id': p.id, 'name': p.name, 'type': 'project'} for p in projects]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
