from flask import render_template, request, redirect, url_for, jsonify
from app import app, db
from datetime import date
import models

import logging
logging.basicConfig(level=logging.DEBUG)

logging.debug("Importation de routes.py")

@app.route('/test')
def test():
    logging.debug("Accès à la route /test")
    return "Test route is working!"

@app.route('/test2')
def test2():
    logging.debug("Accès à la route /test2")
    return "Test2 route is working!"

@app.route('/')
def index():
    logging.debug("Accès à la route /")
    projects = models.Project.query.all()
    tasks = models.Task.query.filter(
        (models.Task.due_date == date.today()) |
        (models.Task.planned_date == date.today())
    ).all()
    funds = models.Funds.query.first().amount if models.Funds.query.first() else 1000
    return render_template('index.html', projects=projects, tasks=tasks, funds=funds)

@app.route('/update_funds', methods=['POST'])
def update_funds():
    logging.debug("Accès à la route /update_funds")
    funds = request.form['funds']
    funds_record = models.Funds.query.first()
    if funds_record:
        funds_record.amount = funds
    else:
        new_funds = models.Funds(amount=funds)
        db.session.add(new_funds)
    db.session.commit()
    return redirect(url_for('index'))

# Routes Tasks
@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        name = request.form.get('name')
        planned_date = request.form.get('planned_date', date.today())
        due_date = request.form.get('due_date')
        recurrence = request.form.get('recurrence')
        time_required = request.form.get('time_required', 0)
        time_required_unit = request.form.get('time_required_unit', 'hours')
        funding = request.form.get('funding', 0)
        benefits = request.form.get('benefits', 0)
        time_to_sell = request.form.get('time_to_sell', 0)
        time_to_sell_unit = request.form.get('time_to_sell_unit', 'hours')

        new_task = models.Task(
            name=name,
            planned_date=planned_date,
            due_date=due_date,
            recurrence=recurrence,
            time_required=time_required,
            time_required_unit=time_required_unit,
            funding=funding,
            benefits=benefits,
            time_to_sell=time_to_sell,
            time_to_sell_unit=time_to_sell_unit
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('tasks/create.html')

@app.route('/tasks/list')
def list_tasks():
    tasks = models.Task.query.all()
    return render_template('tasks/list.html', tasks=tasks)

@app.route('/tasks/<int:id>/details')
def task_details(id):
    task = models.Task.query.get_or_404(id)
    return render_template('tasks/details.html', task=task)

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
def edit_task(id):
    task = models.Task.query.get_or_404(id)
    if request.method == 'POST':
        task.name = request.form.get('name', task.name)
        task.planned_date = request.form.get('planned_date', task.planned_date)
        task.due_date = request.form.get('due_date', task.due_date)
        task.recurrence = request.form.get('recurrence', task.recurrence)
        task.time_required = request.form.get('time_required', task.time_required)
        task.time_required_unit = request.form.get('time_required_unit', task.time_required_unit)
        task.funding = request.form.get('funding', task.funding)
        task.benefits = request.form.get('benefits', task.benefits)
        task.time_to_sell = request.form.get('time_to_sell', task.time_to_sell)
        task.time_to_sell_unit = request.form.get('time_to_sell_unit', task.time_to_sell_unit)

        db.session.commit()
        return redirect(url_for('list_tasks'))
    return render_template('tasks/edit.html', task=task)

@app.route('/tasks/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = models.Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('list_tasks'))

@app.route('/tasks/<int:id>/mark_done', methods=['GET'])
def mark_task_done(id):
    task = models.Task.query.get_or_404(id)
    task.is_done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:id>/mark_undone', methods=['GET'])
def mark_task_undone(id):
    task = models.Task.query.get_or_404(id)
    task.is_done = False
    db.session.commit()
    return redirect(url_for('index'))

# Routes Projects
@app.route('/projects/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        goal = request.form.get('goal', '')
        principle = request.form.get('principle', '')
        protocol = request.form.get('protocol', '')
        prerequisites = request.form.get('prerequisites', '')
        protections = request.form.get('protections', '')
        materials = request.form.get('materials', '')
        consumables = request.form.get('consumables', '')
        time_required = request.form.get('time_required', 0)
        time_required_unit = request.form.get('time_required_unit', 'hours')
        funding = request.form.get('funding', 0)
        time_to_sell = request.form.get('time_to_sell', 0)
        time_to_sell_unit = request.form.get('time_to_sell_unit', 'hours')

        new_project = models.Project(
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
        return redirect(url_for('index'))
    return render_template('projects/create.html')

@app.route('/projects/list')
def list_projects():
    projects = models.Project.query.all()
    return render_template('projects/list.html', projects=projects)

@app.route('/projects/<int:id>/details')
def project_details(id):
    project = models.Project.query.get_or_404(id)
    return render_template('projects/details.html', project=project)

@app.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = models.Project.query.get_or_404(id)
    if request.method == 'POST':
        project.name = request.form.get('name', project.name)
        project.goal = request.form.get('goal', project.goal)
        project.principle = request.form.get('principle', project.principle)
        project.protocol = request.form.get('protocol', project.protocol)
        project.prerequisites = request.form.get('prerequisites', project.prerequisites)
        project.protections = request.form.get('protections', project.protections)
        project.materials = request.form.get('materials', project.materials)
        project.consumables = request.form.get('consumables', project.consumables)
        project.time_required = request.form.get('time_required', project.time_required)
        project.time_required_unit = request.form.get('time_required_unit', project.time_required_unit)
        project.funding = request.form.get('funding', project.funding)
        project.time_to_sell = request.form.get('time_to_sell', project.time_to_sell)
        project.time_to_sell_unit = request.form.get('time_to_sell_unit', project.time_to_sell_unit)

        db.session.commit()
        return redirect(url_for('list_projects'))
    return render_template('projects/edit.html', project=project)

@app.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = models.Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('list_projects'))

# Routes Materials
@app.route('/materials/create', methods=['GET', 'POST'])
def create_material():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', 0)
        new_material = models.Material(name=name, quantity=quantity)
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/create.html')

@app.route('/materials/list')
def list_materials():
    materials = models.Material.query.all()
    return render_template('materials/list.html', materials=materials)

@app.route('/materials/<int:id>/details')
def material_details(id):
    material = models.Material.query.get_or_404(id)
    return render_template('materials/details.html', material=material)

@app.route('/materials/<int:id>/edit', methods=['GET', 'POST'])
def edit_material(id):
    material = models.Material.query.get_or_404(id)
    if request.method == 'POST':
        material.name = request.form.get('name', material.name)
        material.quantity = request.form.get('quantity', material.quantity)
        db.session.commit()
        return redirect(url_for('list_materials'))
    return render_template('materials/edit.html', material=material)

@app.route('/materials/<int:id>/delete', methods=['POST'])
def delete_material(id):
    material = models.Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('list_materials'))

# Routes Consumables
@app.route('/consumables/create', methods=['GET', 'POST'])
def create_consumable():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', 0)
        new_consumable = models.Consumable(name=name, quantity=quantity)
        db.session.add(new_consumable)
        db.session.commit()
        return redirect(url_for('list_consumables'))
    return render_template('consumables/create.html')

@app.route('/consumables/list')
def list_consumables():
    consumables = models.Consumable.query.all()
    return render_template('consumables/list.html', consumables=consumables)

@app.route('/consumables/<int:id>/details')
def consumable_details(id):
    consumable = models.Consumable.query.get_or_404(id)
    return render_template('consumables/details.html', consumable=consumable)

@app.route('/consumables/<int:id>/edit', methods=['GET', 'POST'])
def edit_consumable(id):
    consumable = models.Consumable.query.get_or_404(id)
    if request.method == 'POST':
        consumable.name = request.form.get('name', consumable.name)
        consumable.quantity = request.form.get('quantity', consumable.quantity)
        db.session.commit()
        return redirect(url_for('list_consumables'))
    return render_template('consumables/edit.html', consumable=consumable)

@app.route('/consumables/<int:id>/delete', methods=['POST'])
def delete_consumable(id):
    consumable = models.Consumable.query.get_or_404(id)
    db.session.delete(consumable)
    db.session.commit()
    return redirect(url_for('list_consumables'))

# Routes protections
@app.route('/protections/list')
def list_protections():
    protections = models.Protection.query.all()
    return render_template('protections/list.html', protections=protections)

@app.route('/protections/create', methods=['GET', 'POST'])
def create_protection():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity', 0)
        new_protection = models.Protection(name=name, quantity=quantity)
        db.session.add(new_protection)
        db.session.commit()
        return redirect(url_for('list_protections'))
    return render_template('protections/create.html')

@app.route('/protections/<int:id>/details')
def protection_details(id):
    protection = models.Protection.query.get_or_404(id)
    return render_template('protections/details.html', protection=protection)

@app.route('/protections/<int:id>/edit', methods=['GET', 'POST'])
def edit_protection(id):
    protection = models.Protection.query.get_or_404(id)
    if request.method == 'POST':
        protection.name = request.form.get('name', protection.name)
        protection.quantity = request.form.get('quantity', protection.quantity)
        db.session.commit()
        return redirect(url_for('list_protections'))
    return render_template('protections/edit.html', protection=protection)

@app.route('/protections/<int:id>/delete', methods=['POST'])
def delete_protection(id):
    protection = models.Protection.query.get_or_404(id)
    db.session.delete(protection)
    db.session.commit()
    return redirect(url_for('list_protections'))

# Autocomplétions
@app.route('/autocomplete/protections', methods=['GET'])
def autocomplete_protections():
    query = request.args.get('query', '')
    protections = models.Protection.query.filter(models.Protection.name.ilike(f'%{query}%')).all()
    results = [{'id': p.id, 'name': p.name} for p in protections]
    return jsonify(results)

@app.route('/autocomplete/materials', methods=['GET'])
def autocomplete_materials():
    query = request.args.get('query', '')
    materials = models.Material.query.filter(models.Material.name.ilike(f'%{query}%')).all()
    results = [{'id': m.id, 'name': m.name} for m in materials]
    return jsonify(results)

@app.route('/autocomplete/consumables', methods=['GET'])
def autocomplete_consumables():
    query = request.args.get('query', '')
    consumables = models.Consumable.query.filter(models.Consumable.name.ilike(f'%{query}%')).all()
    results = [{'id': c.id, 'name': c.name} for c in consumables]
    return jsonify(results)

@app.route('/autocomplete/prerequisites', methods=['GET'])
def autocomplete_prerequisites():
    query = request.args.get('query', '')
    tasks = models.Task.query.filter(models.Task.name.ilike(f'%{query}%')).all()
    projects = models.Project.query.filter(models.Project.name.ilike(f'%{query}%')).all()
    results = [{'id': t.id, 'name': t.name, 'type': 'task'} for t in tasks]
    results += [{'id': p.id, 'name': p.name, 'type': 'project'} for p in projects]
    return jsonify(results)

print("Routes importé")
