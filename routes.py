from flask import render_template, request, redirect, url_for, jsonify
from app import app, db
from datetime import date, datetime
from models import *
import math

import logging
logging.basicConfig(level=logging.DEBUG)

logging.debug("Importation de routes.py")
import math
from datetime import datetime, timedelta

import math
from datetime import datetime, timedelta

def update_priorities(item):
    today = datetime.today().date()

    # Assurez-vous que les attributs sont correctement convertis en float ou int
    funding = float(item.funding) if item.funding else 0.0
    time_required = int(item.time_required) if item.time_required else 0
    time_to_sell = int(item.time_to_sell) if item.time_to_sell else 0
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
@app.route('/')
def index():
    logging.debug("Accès à la route /")
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    today = date.today()
    tasks = Task.query.filter(
        (Task.due_date <= today) | (Task.planned_date <= today)
    ).order_by(getattr(Task, sort_by).desc() if direction == 'desc' else getattr(Task, sort_by).asc()).all()
    funds = Funds.query.first().amount if Funds.query.first() else 1000
    return render_template('index.html', daily_tasks=tasks, funds=funds, today=today, sort_by=sort_by, direction=direction)


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

# Routes Tasks
@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            due_date_str = request.form.get('due_date')
            planned_date_str = request.form.get('planned_date')
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date() if planned_date_str else None

            new_task = Task(
                name=name,
                due_date=due_date,
                planned_date=planned_date,
                recurrence=request.form.get('recurrence'),
                time_required=float(request.form.get('time_required', 0.0)) if request.form.get('time_required') else 0.0,
                time_required_unit=request.form.get('time_required_unit', 'seconds'),
                funding=float(request.form.get('funding', 0.0)) if request.form.get('funding') else 0.0,
                benefits=float(request.form.get('benefits', 0.0)) if request.form.get('benefits') else 0.0,
                time_to_sell=float(request.form.get('time_to_sell', 0.0)) if request.form.get('time_to_sell') else 0.0,
                time_to_sell_unit=request.form.get('time_to_sell_unit', 'seconds'),
                urgency=float(request.form.get('urgency', 0.0)) if request.form.get('urgency') else 0.0,
                impact=float(request.form.get('impact', 0.0)) if request.form.get('impact') else 0.0,
                resources=float(request.form.get('resources', 0.0)) if request.form.get('resources') else 0.0,
                complexity=float(request.form.get('complexity', 0.0)) if request.form.get('complexity') else 0.0,
                alignment=float(request.form.get('alignment', 0.0)) if request.form.get('alignment') else 0.0,
                order=int(request.form.get('order', 0)) if request.form.get('order') else 0
            )

            new_task.is_daily = new_task.check_if_daily()
            db.session.add(new_task)
            db.session.commit()

            # Ajout des ressources
            material_names = request.form.getlist('material_names[]')
            material_quantities = request.form.getlist('material_quantities[]')
            if material_names:
                if not material_quantities:
                    material_quantities = [1] * len(material_names)
                for name, quantity in zip(material_names, material_quantities):
                    if name.strip():
                        material, quantity_needed = check_and_create_resource(Material, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=new_task.id, resource_id=material.id, resource_type='Material', quantity=quantity_needed)
                        db.session.add(task_resource)

            consumable_names = request.form.getlist('consumable_names[]')
            consumable_quantities = request.form.getlist('consumable_quantities[]')
            if consumable_names:
                if not consumable_quantities:
                    consumable_quantities = [1] * len(consumable_names)
                for name, quantity in zip(consumable_names, consumable_quantities):
                    if name.strip():
                        consumable, quantity_needed = check_and_create_resource(Consumable, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=new_task.id, resource_id=consumable.id, resource_type='Consumable', quantity=quantity_needed)
                        db.session.add(task_resource)

            protection_names = request.form.getlist('protection_names[]')
            protection_quantities = request.form.getlist('protection_quantities[]')
            if protection_names:
                if not protection_quantities:
                    protection_quantities = [1] * len(protection_names)
                for name, quantity in zip(protection_names, protection_quantities):
                    if name.strip():
                        protection, quantity_needed = check_and_create_resource(Protection, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=new_task.id, resource_id=protection.id, resource_type='Protection', quantity=quantity_needed)
                        db.session.add(task_resource)

            db.session.commit()
            return redirect(url_for('index'))
        except ValueError as e:
            logging.error(f"Erreur de conversion des données : {str(e)}")
            return render_template('tasks/create.html', error=str(e))
    return render_template('tasks/create.html')


@app.route('/tasks/list', methods=['GET'])
def list_tasks():
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    try:
        tasks = Task.query.order_by(getattr(Task, sort_by).desc() if direction == 'desc' else getattr(Task, sort_by).asc()).all()
    except AttributeError:
        tasks = Task.query.order_by(Task.name.asc()).all()
    return render_template('tasks/list.html', tasks=tasks, sort_by=sort_by, direction=direction)

@app.route('/tasks/<int:id>/details', methods=['GET'])
def task_details(id):
    task = Task.query.get_or_404(id)
    return render_template('tasks/details.html', task=task)

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        try:
            task.name = request.form.get('name', task.name)
            due_date_str = request.form.get('due_date')
            planned_date_str = request.form.get('planned_date')

            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            task.planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date() if planned_date_str else None

            task.recurrence = request.form.get('recurrence', task.recurrence)
            task.time_required = float(request.form.get('time_required', 0)) if request.form.get('time_required') else task.time_required
            task.time_required_unit = request.form.get('time_required_unit', task.time_required_unit)
            task.funding = float(request.form.get('funding', 0)) if request.form.get('funding') else task.funding
            task.benefits = float(request.form.get('benefits', 0)) if request.form.get('benefits') else task.benefits
            task.time_to_sell = float(request.form.get('time_to_sell', 0)) if request.form.get('time_to_sell') else task.time_to_sell
            task.time_to_sell_unit = request.form.get('time_to_sell_unit', task.time_to_sell_unit)
            task.urgency = float(request.form.get('urgency', 0)) if request.form.get('urgency') else task.urgency
            task.impact = float(request.form.get('impact', 0)) if request.form.get('impact') else task.impact
            task.resources = float(request.form.get('resources', 0)) if request.form.get('resources') else task.resources
            task.complexity = float(request.form.get('complexity', 0)) if request.form.get('complexity') else task.complexity
            task.alignment = float(request.form.get('alignment', 0)) if request.form.get('alignment') else task.alignment
            task.order = int(request.form.get('order', 0)) if request.form.get('order') else task.order

            task.is_daily = task.check_if_daily()

            db.session.commit()

            # Mise à jour des ressources
            db.session.query(TaskResource).filter_by(task_id=task.id).delete()

            material_names = request.form.getlist('material_names[]')
            material_quantities = request.form.getlist('material_quantities[]')
            if material_names:
                if not material_quantities:
                    material_quantities = [1] * len(material_names)
                for name, quantity in zip(material_names, material_quantities):
                    if name.strip():
                        material, quantity_needed = check_and_create_resource(Material, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=task.id, resource_id=material.id, resource_type='Material', quantity=quantity_needed)
                        db.session.add(task_resource)

            consumable_names = request.form.getlist('consumable_names[]')
            consumable_quantities = request.form.getlist('consumable_quantities[]')
            if consumable_names:
                if not consumable_quantities:
                    consumable_quantities = [1] * len(consumable_names)
                for name, quantity in zip(consumable_names, consumable_quantities):
                    if name.strip():
                        consumable, quantity_needed = check_and_create_resource(Consumable, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=task.id, resource_id=consumable.id, resource_type='Consumable', quantity=quantity_needed)
                        db.session.add(task_resource)

            protection_names = request.form.getlist('protection_names[]')
            protection_quantities = request.form.getlist('protection_quantities[]')
            if protection_names:
                if not protection_quantities:
                    protection_quantities = [1] * len(protection_names)
                for name, quantity in zip(protection_names, protection_quantities):
                    if name.strip():
                        protection, quantity_needed = check_and_create_resource(Protection, name, int(quantity) if quantity else 1)
                        task_resource = TaskResource(task_id=task.id, resource_id=protection.id, resource_type='Protection', quantity=quantity_needed)
                        db.session.add(task_resource)

            db.session.commit()
            return redirect(url_for('index'))
        except ValueError as e:
            logging.error(f"Erreur de conversion des données : {str(e)}")
            return render_template('tasks/edit.html', task=task, error=str(e))
    return render_template('tasks/edit.html', task=task)


@app.route('/tasks/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('list_tasks'))

@app.route('/tasks/<int:id>/mark_done', methods=['GET'])
def mark_task_done(id):
    task = Task.query.get_or_404(id)
    task.is_done = True
    db.session.commit()
    return redirect(url_for('index'))

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
        goal = request.form['goal']
        principle = request.form['principle']
        protocol = request.form['protocol']
        time_required = int(request.form['time_required']) if request.form['time_required'] else 0
        time_required_unit = request.form['time_required_unit']
        funding = float(request.form['funding']) if request.form['funding'] else 0.0
        benefits = float(request.form['benefits']) if request.form['benefits'] else 0.0
        time_to_sell = int(request.form['time_to_sell']) if request.form['time_to_sell'] else 0
        time_to_sell_unit = request.form['time_to_sell_unit']

        due_date_str = request.form['due_date']
        planned_date_str = request.form['planned_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date() if planned_date_str else None

        new_project = Project(
            name=name, goal=goal, principle=principle, protocol=protocol,
            time_required=time_required, time_required_unit=time_required_unit,
            funding=funding, benefits=benefits, time_to_sell=time_to_sell,
            time_to_sell_unit=time_to_sell_unit, due_date=due_date, planned_date=planned_date
        )

        db.session.add(new_project)
        db.session.commit()

        # Ajout des ressources
        material_names = request.form.getlist('material_names[]')
        material_quantities = request.form.getlist('material_quantities[]')
        if material_names:
            if not material_quantities:
                material_quantities = [1] * len(material_names)
            for name, quantity in zip(material_names, material_quantities):
                if name.strip():
                    material, quantity_needed = check_and_create_resource(Material, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=new_project.id, resource_id=material.id, resource_type='Material', quantity=quantity_needed)
                    db.session.add(project_resource)

        consumable_names = request.form.getlist('consumable_names[]')
        consumable_quantities = request.form.getlist('consumable_quantities[]')
        if consumable_names:
            if not consumable_quantities:
                consumable_quantities = [1] * len(consumable_names)
            for name, quantity in zip(consumable_names, consumable_quantities):
                if name.strip():
                    consumable, quantity_needed = check_and_create_resource(Consumable, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=new_project.id, resource_id=consumable.id, resource_type='Consumable', quantity=quantity_needed)
                    db.session.add(project_resource)

        protection_names = request.form.getlist('protection_names[]')
        protection_quantities = request.form.getlist('protection_quantities[]')
        if protection_names:
            if not protection_quantities:
                protection_quantities = [1] * len(protection_names)
            for name, quantity in zip(protection_names, protection_quantities):
                if name.strip():
                    protection, quantity_needed = check_and_create_resource(Protection, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=new_project.id, resource_id=protection.id, resource_type='Protection', quantity=quantity_needed)
                    db.session.add(project_resource)

        db.session.commit()
        return redirect(url_for('list_projects'))
    return render_template('projects/create.html')

@app.route('/projects/list', methods=['GET'])
def list_projects():
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    try:
        projects = Project.query.order_by(getattr(Project, sort_by).desc() if direction == 'desc' else getattr(Project, sort_by).asc()).all()
    except AttributeError:
        projects = Project.query.order_by(Project.name.asc()).all()
    return render_template('projects/list.html', projects=projects, sort_by=sort_by, direction=direction)



@app.route('/projects/<int:id>/details', methods=['GET', 'POST'])
def project_details(id):
    project = Project.query.get_or_404(id)
    update_priorities(project)
    if request.method == 'POST':
        task_name = request.form.get('task_name')
        if task_name:
            new_task = Task(
                name=task_name,
                project_id=project.id,
                planned_date=date.today()
            )
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('project_details', id=project.id))
    return render_template('projects/details.html', project=project)

@app.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.name = request.form.get('name', project.name)
        project.goal = request.form.get('goal', project.goal)
        project.principle = request.form.get('principle', project.principle)
        project.protocol = request.form.get('protocol', project.protocol)
        project.time_required = request.form.get('time_required', project.time_required)
        project.time_required_unit = request.form.get('time_required_unit', project.time_required_unit)
        project.funding = request.form.get('funding', project.funding)
        project.benefits = float(request.form.get('benefits', 0)) if request.form.get('benefits') else project.benefits
        project.time_to_sell = request.form.get('time_to_sell', project.time_to_sell)
        project.time_to_sell_unit = request.form.get('time_to_sell_unit', project.time_to_sell_unit)
        due_date_str = request.form.get('due_date')
        planned_date_str = request.form.get('planned_date')
        project.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        project.planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date() if planned_date_str else None

        db.session.commit()

        # Mise à jour des ressources
        db.session.query(ProjectResource).filter_by(project_id=project.id).delete()

        material_names = request.form.getlist('material_names[]')
        material_quantities = request.form.getlist('material_quantities[]')
        if material_names:
            if not material_quantities:
                material_quantities = [1] * len(material_names)
            for name, quantity in zip(material_names, material_quantities):
                if name.strip():
                    material, quantity_needed = check_and_create_resource(Material, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=project.id, resource_id=material.id, resource_type='Material', quantity=quantity_needed)
                    db.session.add(project_resource)

        consumable_names = request.form.getlist('consumable_names[]')
        consumable_quantities = request.form.getlist('consumable_quantities[]')
        if consumable_names:
            if not consumable_quantities:
                consumable_quantities = [1] * len(consumable_names)
            for name, quantity in zip(consumable_names, consumable_quantities):
                if name.strip():
                    consumable, quantity_needed = check_and_create_resource(Consumable, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=project.id, resource_id=consumable.id, resource_type='Consumable', quantity=quantity_needed)
                    db.session.add(project_resource)

        protection_names = request.form.getlist('protection_names[]')
        protection_quantities = request.form.getlist('protection_quantities[]')
        if protection_names:
            if not protection_quantities:
                protection_quantities = [1] * len(protection_names)
            for name, quantity in zip(protection_names, protection_quantities):
                if name.strip():
                    protection, quantity_needed = check_and_create_resource(Protection, name, int(quantity) if quantity else 1)
                    project_resource = ProjectResource(project_id=project.id, resource_id=protection.id, resource_type='Protection', quantity=quantity_needed)
                    db.session.add(project_resource)

        db.session.commit()
        return redirect(url_for('list_projects'))
    return render_template('projects/edit.html', project=project)


@app.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('list_projects'))

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/delete', methods=['POST'])
def delete_project_task(project_id, task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('project_details', id=project_id))

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/mark_done', methods=['GET'])
def mark_project_task_done(project_id, task_id):
    task = Task.query.get_or_404(task_id)
    task.is_done = True
    db.session.commit()
    return redirect(url_for('project_details', id=project_id))

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/mark_undone', methods=['GET'])
def mark_project_task_undone(project_id, task_id):
    task = Task.query.get_or_404(task_id)
    task.is_done = False
    db.session.commit()
    return redirect(url_for('project_details', id=project_id))

# Routes Materials
@app.route('/materials/create', methods=['GET', 'POST'])
def create_material():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', type=int)

        if quantity is None:
            quantity = 0
        new_material = Material(name=name, quantity=quantity)
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/create.html')

@app.route('/materials/list', methods=['GET'])
def list_materials():
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    try:
        materials = Material.query.order_by(getattr(Material, sort_by).desc() if direction == 'desc' else getattr(Material, sort_by).asc()).all()
    except AttributeError:
        materials = Material.query.order_by(Material.name.asc()).all()
    return render_template('materials/list.html', materials=materials, sort_by=sort_by, direction=direction)


@app.route('/materials/<int:id>/details')
def material_details(id):
    material = Material.query.get_or_404(id)
    return render_template('materials/details.html', material=material)

@app.route('/materials/<int:id>/edit', methods=['GET', 'POST'])
def edit_material(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        material.name = request.form.get('name', material.name)
        material.quantity = request.form.get('quantity', material.quantity)
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/edit.html', material=material)

@app.route('/materials/<int:id>/delete', methods=['POST'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('list_materials'))

# Routes Consumables
@app.route('/consumables/create', methods=['GET', 'POST'])
def create_consumable():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', type=int)

        if quantity is None:
            quantity = 0

        new_consumable = Consumable(name=name, quantity=quantity)
        db.session.add(new_consumable)
        db.session.commit()
        return redirect(url_for('list_consumables'))
    return render_template('consumables/create.html')

@app.route('/consumables/list', methods=['GET'])
def list_consumables():
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    try:
        consumables = Consumable.query.order_by(getattr(Consumable, sort_by).desc() if direction == 'desc' else getattr(Consumable, sort_by).asc()).all()
    except AttributeError:
        consumables = Consumable.query.order_by(Consumable.name.asc()).all()
    return render_template('consumables/list.html', consumables=consumables, sort_by=sort_by, direction=direction)

@app.route('/consumables/<int:id>/details')
def consumable_details(id):
    consumable = Consumable.query.get_or_404(id)
    return render_template('consumables/details.html', consumable=consumable)

@app.route('/consumables/<int:id>/edit', methods=['GET', 'POST'])
def edit_consumable(id):
    consumable = Consumable.query.get_or_404(id)
    if request.method == 'POST':
        consumable.name = request.form.get('name', consumable.name)
        consumable.quantity = request.form.get('quantity', consumable.quantity)
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
@app.route('/protections/list', methods=['GET'])
def list_protections():
    sort_by = request.args.get('sort_by', 'name')
    direction = request.args.get('direction', 'asc')
    try:
        protections = Protection.query.order_by(getattr(Protection, sort_by).desc() if direction == 'desc' else getattr(Protection, sort_by).asc()).all()
    except AttributeError:
        protections = Protection.query.order_by(Protection.name.asc()).all()
    return render_template('protections/list.html', protections=protections, sort_by=sort_by, direction=direction)



@app.route('/protections/create', methods=['GET', 'POST'])
def create_protection():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', type=int)

        if quantity is None:
            quantity = 0

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
        protection.name = request.form.get('name', protection.name)
        protection.quantity = request.form.get('quantity', protection.quantity)
        db.session.commit()
        return redirect(url_for('list_protections'))
    return render_template('protections/edit.html', protection=protection)

@app.route('/protections/<int:id>/delete', methods=['POST'])
def delete_protection(id):
    protection = Protection.query.get_or_404(id)
    db.session.delete(protection)
    db.session.commit()
    return redirect(url_for('list_protections'))

# Autocomplétions
@app.route('/autocomplete/protections')
def autocomplete_protections():
    query = request.args.get('query')
    protections = Protection.query.filter(Protection.name.like(f'%{query}%')).all()
    results = [protection.name for protection in protections]
    return jsonify(results)

@app.route('/autocomplete/materials')
def autocomplete_materials():
    query = request.args.get('query')
    materials = Material.query.filter(Material.name.like(f'%{query}%')).all()
    results = [material.name for material in materials]
    return jsonify(results)

@app.route('/autocomplete/consumables')
def autocomplete_consumables():
    query = request.args.get('query')
    consumables = Consumable.query.filter(Consumable.name.like(f'%{query}%')).all()
    results = [consumable.name for consumable in consumables]
    return jsonify(results)

@app.route('/autocomplete/prerequisites')
def autocomplete_prerequisites():
    query = request.args.get('query')
    prerequisites = Project.query.filter(Project.name.like(f'%{query}%')).all()
    results = [prerequisite.name for prerequisite in prerequisites]
    return jsonify(results)

print("Routes importé")
