from flask import render_template, request, redirect, url_for, jsonify, Blueprint
from app import app, db
from datetime import date, datetime
from models import BaseActivity, BaseResource, Task, Project, Protocol, Material, Protection, Consumable, Funds
import math
from sqlalchemy.orm import relationship
import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("Importation de routes.py")

# DEF
def update_priorities(item):
    today = datetime.today().date()

    # Assurez-vous que les attributs sont correctement convertis en float ou int
    funding = float(item.funding) if item.funding else 0.0
    time_required = float(item.time_required) if item.time_required else 0
    time_to_sell = float(item.time_to_sell) if item.time_to_sell else 0.0
    benefits = float(item.benefits) if item.benefits else 0.0

    # Calculer l'urgence
    if item.due_date:
        days_to_due = (item.due_date - today).days
        days_needed = days_to_due - time_required
        item.urgency = round(max(0, min(100, (days_needed / days_to_due) * 100)) if days_to_due != 0 else 100, 2)
    else:
        item.urgency = 0

    # Calculer l'impact
    if benefits and funding and time_required and time_to_sell:
        avg_cost_time = (funding + time_required + time_to_sell) / 3
        item.impact = round((benefits / avg_cost_time) * 50, 2)
        item.impact = max(0, min(100, item.impact))
    else:
        item.impact = 50  # Neutre

    # Calculer les ressources
    available_funds = get_available_funds()
    available_materials = get_available_materials()
    available_protections = get_available_protections()
    available_consumables = get_available_consumables()

    funds_ratio = funding / available_funds if available_funds else 0

    if hasattr(item, 'materials'):
        materials_ratio = sum([min(available_materials.get(mat.name, 0) / mat.quantity, 1) for mat in item.materials]) / len(item.materials) if item.materials else 0
    else:
        materials_ratio = 0

    if hasattr(item, 'protections'):
        protections_ratio = sum([min(available_protections.get(prot.name, 0) / prot.quantity, 1) for prot in item.protections]) / len(item.protections) if item.protections else 0
    else:
        protections_ratio = 0

    if hasattr(item, 'consumables'):
        consumables_ratio = sum([min(available_consumables.get(consum.name, 0) / consum.quantity, 1) for consum in item.consumables]) / len(item.consumables) if item.consumables else 0
    else:
        consumables_ratio = 0

    item.resources = round((funds_ratio + materials_ratio + protections_ratio + consumables_ratio) / 4 * 100, 2)
    item.resources = max(0, min(100, item.resources))

    # Calculer la complexité
    if hasattr(item, 'prerequisites'):
        num_prerequisites = len(item.prerequisites)
        item.complexity = calculate_complexity(num_prerequisites)
    else:
        item.complexity = 0

    # Calculer l'alignement
    if hasattr(item, 'dependent_projects'):
        num_dependents = len(item.dependent_projects)
        dependents_priorities = [dep.priority for dep in item.dependent_projects]
    elif hasattr(item, 'dependents'):
        num_dependents = len(item.dependents)
        dependents_priorities = [dep.priority for dep in item.dependents]
    else:
        num_dependents = 0
        dependents_priorities = []

    item.alignment = calculate_alignment(num_dependents, dependents_priorities)

    # Calculer la priorité totale
    item.priority = round((item.urgency + item.impact + item.resources + (100 - item.complexity) + item.alignment) / 5, 2)

    db.session.commit()
def check_and_create_resource(model, name):
    resource = model.query.filter_by(name=name).first()
    if not resource:
        resource = model(name=name, quantity=0)
        db.session.add(resource)
        db.session.commit()
    return resource
def calculate_complexity(num_prerequisites, k=5):
    """
    Calcul de la complexité en utilisant une fonction logarithmique.
    """
    complexity = 100 * math.log(1 + num_prerequisites) / math.log(1 + num_prerequisites + k)
    return round(complexity, 2)
def calculate_alignment(num_dependents, dependents_priorities, k=5):
    """
    Calcul de l'alignement en utilisant une fonction logarithmique et la priorité moyenne des dépendants.
    """
    avg_priority_of_dependents = sum(dependents_priorities) / len(dependents_priorities) if dependents_priorities else 0
    alignment = 100 * math.log(1 + num_dependents) / math.log(1 + num_dependents + k) + avg_priority_of_dependents / 2
    return round(alignment, 2)
def get_available_funds():
    """
    Obtient les fonds disponibles.
    """
    funds = Funds.query.first()
    return funds.amount if funds else 0.0
def get_available_materials():
    """
    Obtient les matériaux disponibles.
    """
    materials = Material.query.all()
    return {material.name: material.quantity for material in materials}
def get_available_protections():
    """
    Obtient les protections disponibles.
    """
    protections = Protection.query.all()
    return {protection.name: protection.quantity for protection in protections}
def get_available_consumables():
    """
    Obtient les consommables disponibles.
    """
    consumables = Consumable.query.all()
    return {consumable.name: consumable.quantity for consumable in consumables}
    db.session.commit()
def check_and_create_resource(model, name, quantity_needed=1):
    resource = model.query.filter_by(name=name).first()
    if not resource:
        resource = model(name=name, quantity=0)
        db.session.add(resource)
        db.session.commit()
    return resource, quantity_needed
def validate_prerequisites(item):
    if isinstance(item, Task):
        for prereq in item.prerequisites:
            if not isinstance(prereq, Task):
                raise ValidationError("A task's prerequisite must be another task.")
    elif isinstance(item, Project):
        for prereq in item.prerequisites:
            if not isinstance(prereq, Project):
                raise ValidationError("A project's prerequisite must be another project.")

class BaseRoute:
    def __init__(self, blueprint_name, model_class):
        self.blueprint = Blueprint(blueprint_name, __name__)
        self.model_class = model_class
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route('/')
        def list_items():
            sort_by = request.args.get('sort_by', 'name')
            direction = request.args.get('direction', 'asc')
            try:
                items = self.model_class.query.order_by(
                    getattr(self.model_class, sort_by).desc() if direction == 'desc' else getattr(self.model_class, sort_by).asc()
                ).all()
            except AttributeError:
                items = self.model_class.query.order_by(self.model_class.name.asc()).all()
            return render_template(f'{self.model_class.__tablename__}/list.html', items=items, sort_by=sort_by, direction=direction)

        @self.blueprint.route('/create', methods=['GET', 'POST'])
        def create_item():
            if request.method == 'POST':
                try:
                    item = self.model_class(**request.form.to_dict())
                    db.session.add(item)
                    db.session.commit()
                    return redirect(url_for(f'.list_items'))
                except ValueError as e:
                    return render_template(f'{self.model_class.__tablename__}/create.html', error=str(e))
            return render_template(f'{self.model_class.__tablename__}/create.html')

        @self.blueprint.route('/<int:id>/details')
        def item_details(id):
            item = self.model_class.query.get_or_404(id)
            return render_template(f'{self.model_class.__tablename__}/details.html', item=item)

        @self.blueprint.route('/<int:id>/edit', methods=['GET', 'POST'])
        def edit_item(id):
            item = self.model_class.query.get_or_404(id)
            if request.method == 'POST':
                try:
                    for key, value in request.form.items():
                        setattr(item, key, value)
                    db.session.commit()
                    return redirect(url_for(f'.list_items'))
                except ValueError as e:
                    return render_template(f'{self.model_class.__tablename__}/edit.html', item=item, error=str(e))
            return render_template(f'{self.model_class.__tablename__}/edit.html', item=item)

        @self.blueprint.route('/<int:id>/delete', methods=['POST'])
        def delete_item(id):
            item = self.model_class.query.get_or_404(id)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for(f'.list_items'))

class FundsRoute(BaseRoute):
    def add_routes(self):
        super().add_routes()

        @self.blueprint.route('/update_funds', methods=['POST'])
        def update_funds():
            logging.debug("Accès à la route /update_funds")
            funds = request.form['funds']
            funds_record = Funds.query.first()
            if funds_record:
                funds_record.amount = funds
            else:
                new_funds = Funds(name="General Funds", amount=funds)
                db.session.add(new_funds)
            db.session.commit()
            return redirect(url_for('index'))
# Instantiate and register the funds route

# Routes Tasks

class TaskRoute(BaseRoute):
    def add_routes(self):
        super().add_routes()

        @self.blueprint.route('/<int:id>/mark_done', methods=['GET'])
        def mark_task_done(id):
            task = self.model_class.query.get_or_404(id)
            task.is_done = True
            db.session.commit()
            return redirect(url_for('index'))

        @self.blueprint.route('/<int:id>/mark_undone', methods=['GET'])
        def mark_task_undone(id):
            task = self.model_class.query.get_or_404(id)
            task.is_done = False
            db.session.commit()
            return redirect(url_for('index'))

        @self.blueprint.route('/select_protocol', methods=['GET'])
        def select_protocol_for_task():
            return render_template('tasks/select_protocol.html')

        @self.blueprint.route('/create_from_protocol', methods=['POST'])
        def create_task_from_protocol():
            protocol_id = request.form.get('protocol_id')
            protocol = Protocol.query.get(protocol_id)
            return render_template('tasks/create.html', protocol=protocol)

# Routes Projects
class ProjectRoute(BaseRoute):
    def add_routes(self):
        super().add_routes()

        @self.blueprint.route('/<int:id>/tasks/<int:task_id>/delete', methods=['POST'])
        def delete_project_task(id, task_id):
            task = Task.query.get_or_404(task_id)
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for(f'{self.blueprint.name}.item_details', id=id))

        @self.blueprint.route('/<int:id>/tasks/<int:task_id>/mark_done', methods=['GET'])
        def mark_project_task_done(id, task_id):
            task = Task.query.get_or_404(task_id)
            task.is_done = True
            db.session.commit()
            return redirect(url_for(f'{self.blueprint.name}.item_details', id=id))

        @self.blueprint.route('/<int:id>/tasks/<int:task_id>/mark_undone', methods=['GET'])
        def mark_project_task_undone(id, task_id):
            task = Task.query.get_or_404(task_id)
            task.is_done = False
            db.session.commit()
            return redirect(url_for(f'{self.blueprint.name}.item_details', id=id))

        @self.blueprint.route('/<int:id>/mark_done', methods=['GET'])
        def mark_project_done(id):
            project = self.model_class.query.get_or_404(id)
            project.is_done = True
            db.session.commit()
            create_protocol_from_project(project)
            return redirect(url_for('index'))

# ROUTES PROTOCOLS
class ProtocolRoute(BaseRoute):
    def add_routes(self):
        super().add_routes()

        @self.blueprint.route('/select_project', methods=['GET'])
        def select_project_for_protocol():
            return render_template('protocol/select_project.html')

        @self.blueprint.route('/create_from_project', methods=['POST'])
        def create_protocol_from_project():
            project_id = request.form.get('project_id')
            project = Project.query.get(project_id)
            return render_template('protocol/create.html', project=project)

# Routes RESSOUCES
class MaterialRoute(BaseRoute):
    pass

class ConsumableRoute(BaseRoute):
    pass

class ProtectionRoute(BaseRoute):
    pass

# Instancier et enregistrer les routes
task_routes = TaskRoute('tasks', Task)
project_routes = ProjectRoute('projects', Project)
protocol_routes = ProtocolRoute('protocols', Protocol)
material_routes = MaterialRoute('materials', Material)
consumable_routes = ConsumableRoute('consumables', Consumable)
protection_routes = ProtectionRoute('protections', Protection)
funds_routes = FundsRoute('funds', Funds)

app.register_blueprint(task_routes.blueprint, url_prefix='/tasks')
app.register_blueprint(project_routes.blueprint, url_prefix='/projects')
app.register_blueprint(protocol_routes.blueprint, url_prefix='/protocols')
app.register_blueprint(material_routes.blueprint, url_prefix='/materials')
app.register_blueprint(consumable_routes.blueprint, url_prefix='/consumables')
app.register_blueprint(protection_routes.blueprint, url_prefix='/protections')
app.register_blueprint(funds_routes.blueprint, url_prefix='/funds')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_funds', methods=['POST'])
def update_funds():
    logging.debug("Accès à la route /update_funds")
    funds = request.form['funds']
    funds_record = Funds.query.first()
    if funds_record:
        funds_record.amount = funds
    else:
        new_funds = Funds(amount=funds)
        db.session.add(new_funds)
    db.session.commit()
    return redirect(url_for('index'))

# Autocomplétions

def autocomplete(model, field_name='name'):
    query = request.args.get('query', '')
    filter_expression = getattr(model, field_name).like(f'%{query}%')
    results = model.query.filter(filter_expression).all()
    return jsonify([getattr(item, field_name) for item in results])

@app.route('/autocomplete/<model_name>', methods=['GET'])
def autocomplete_generic(model_name):
    models = {
        'protections': Protection,
        'materials': Material,
        'consumables': Consumable,
        'prerequisites': Project,
        'tasks': Task,
        'projects': Project,
        'protocols': Protocol
    }
    model = models.get(model_name)
    if model:
        return autocomplete(model)
    return jsonify([]), 404

@app.route('/autocomplete/protections', methods=['GET'])
def autocomplete_protections():
    return autocomplete(Protection)

@app.route('/autocomplete/materials', methods=['GET'])
def autocomplete_materials():
    return autocomplete(Material)

@app.route('/autocomplete/consumables', methods=['GET'])
def autocomplete_consumables():
    return autocomplete(Consumable)

@app.route('/autocomplete/prerequisites', methods=['GET'])
def autocomplete_prerequisites():
    return autocomplete(Project)

@app.route('/autocomplete/tasks', methods=['GET'])
def autocomplete_tasks():
    return autocomplete(Task)

@app.route('/autocomplete/projects', methods=['GET'])
def autocomplete_projects():
    return autocomplete(Project)

@app.route('/autocomplete/protocols', methods=['GET'])
def autocomplete_protocols():
    return autocomplete(Protocol)


print("Routes importé")
