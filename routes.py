from flask import render_template, request, redirect, url_for
from app import app, db
import models

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