@app.route('/')
def index():
    logging.debug("Accès à la route /")
    try:
        sort_by = request.args.get('sort_by', 'name')
        direction = request.args.get('direction', 'asc')
        today = date.today()

        tasks = Task.query.filter(
            (Task.due_date <= today) | (Task.planned_date <= today)
        ).order_by(getattr(Task, sort_by).desc() if direction == 'desc' else getattr(Task, sort_by).asc()).all()

        funds = Funds.query.first().amount if Funds.query.first() else 1000

    except Exception as e:
        logging.error(f"Erreur lors de l'accès à la route / : {e}")
        return render_template('error.html', error=str(e))

    return render_template('index.html', daily_tasks=tasks, funds=funds, today=today, sort_by=sort_by, direction=direction)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Accueil</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="container">
        <h1>Accueil</h1>
        <nav>
            <ul>
                <li><a href="/">Accueil</a></li>
                <li>Tâches :</li>
                <ul>
                    <li><a href="/tasks/list">Liste des tâches</a></li>
                    <li><a href="/tasks/create">Créer une tâche</a></li>
                </ul>
                <li>Projets :</li>
                <ul>
                    <li><a href="/projects/list">Liste des projets</a></li>
                    <li><a href="/projects/create">Créer un projet</a></li>
                </ul>
                <li>Protocols :</li>
                <ul>
                    <li><a href="/protocols/list">Liste des protocoles</a></li>
                    <li><a href="/protocols/select_type">Créer un protocole</a></li>
                </ul>
                <li>Protections :</li>
                <ul>
                    <li><a href="/protections/list">Liste des protections</a></li>
                    <li><a href="/protections/create">Créer une protection</a></li>
                </ul>
                <li>Matériels :</li>
                <ul>
                    <li><a href="/materials/list">Liste des matériels</a></li>
                    <li><a href="/materials/create">Créer un matériel</a></li>
                </ul>
                <li>Consommables :</li>
                <ul>
                    <li><a href="/consumables/list">Liste des consommables</a></li>
                    <li><a href="/consumables/create">Créer un consommable</a></li>
                </ul>
            </ul>
        </nav>
        <h2>Argent disponible</h2>
        <form action="/update_funds" method="post">
            <label for="funds">Montant: </label>
            <input type="number" id="funds" name="funds" value="{{ funds }}">
            <button type="submit">Mettre à jour</button>
        </form>
        <h2>Tâches journalières</h2>
        <h3>Tâches à faire</h3>
        <table>
            <thead>
                <tr>
                    <th><a href="?sort_by=name&direction={{ 'desc' if sort_by == 'name' and direction == 'asc' else 'asc' }}">Nom</a></th>
                    <th><a href="?sort_by=project&direction={{ 'desc' if sort_by == 'project' and direction == 'asc' else 'asc' }}">Projet</a></th>
                    <th><a href="?sort_by=priority&direction={{ 'desc' if sort_by == 'priority' and direction == 'asc' else 'asc' }}">Priorité</a></th>
                    <th><a href="?sort_by=urgency&direction={{ 'desc' if sort_by == 'urgency' and direction == 'asc' else 'asc' }}">Urgence</a></th>
                    <th><a href="?sort_by=impact&direction={{ 'desc' if sort_by == 'impact' and direction == 'asc' else 'asc' }}">Impact</a></th>
                    <th><a href="?sort_by=resources&direction={{ 'desc' if sort_by == 'resources' and direction == 'asc' else 'asc' }}">Ressources</a></th>
                    <th><a href="?sort_by=complexity&direction={{ 'desc' if sort_by == 'complexity' and direction == 'asc' else 'asc' }}">Complexité</a></th>
                    <th><a href="?sort_by=alignment&direction={{ 'desc' if sort_by == 'alignment' and direction == 'asc' else 'asc' }}">Alignement</a></th>
                    <th><a href="?sort_by=due_date&direction={{ 'desc' if sort_by == 'due_date' and direction == 'asc' else 'asc' }}">Date d'échéance</a></th>
                    <th><a href="?sort_by=planned_date&direction={{ 'desc' if sort_by == 'planned_date' and direction == 'asc' else 'asc' }}">Date de réalisation</a></th>
                    <th><a href="?sort_by=recurrence&direction={{ 'desc' if sort_by == 'recurrence' and direction == 'asc' else 'asc' }}">Récurrence</a></th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for task in daily_tasks if not task.is_done %}
                <tr>
                    <td>{{ task.name }}</td>
                    <td>{{ task.project.name if task.project else "Indépendant" }}</td>
                    <td>{{ "%.2f"|format(task.priority) }}%</td>
                    <td>{{ "%.2f"|format(task.urgency) }}%</td>
                    <td>{{ "%.2f"|format(task.impact) }}%</td>
                    <td>{{ "%.2f"|format(task.resources) }}%</td>
                    <td>{{ "%.2f"|format(task.complexity) }}%</td>
                    <td>{{ "%.2f"|format(task.alignment) }}%</td>
                    <td>{{ task.due_date if task.due_date else "Aucune" }}</td>
                    <td>{{ task.planned_date if task.planned_date else "Aucune" }}</td>
                    <td>{{ task.recurrence if task.recurrence else "Aucune" }}</td>
                    <td>
                        <a href="/tasks/{{ task.id }}/mark_done">Fait ?</a>
                        <a href="/tasks/{{ task.id }}/details">Détails</a>
                        <a href="/tasks/{{ task.id }}/edit">Modifier</a>
                        <form action="{{ url_for('delete_task', id=task.id) }}" method="post" style="display:inline;">
                            <button type="submit">Supprimer</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <h3>Tâches faites</h3>
        <table>
            <thead>
                <tr>
                    <th><a href="?sort_by=name&direction={{ 'desc' if sort_by == 'name' and direction == 'asc' else 'asc' }}">Nom</a></th>
                    <th><a href="?sort_by=project&direction={{ 'desc' if sort_by == 'project' and direction == 'asc' else 'asc' }}">Projet</a></th>
                    <th><a href="?sort_by=priority&direction={{ 'desc' if sort_by == 'priority' and direction == 'asc' else 'asc' }}">Priorité</a></th>
                    <th><a href="?sort_by=urgency&direction={{ 'desc' if sort_by == 'urgency' and direction == 'asc' else 'asc' }}">Urgence</a></th>
                    <th><a href="?sort_by=impact&direction={{ 'desc' if sort_by == 'impact' and direction == 'asc' else 'asc' }}">Impact</a></th>
                    <th><a href="?sort_by=resources&direction={{ 'desc' if sort_by == 'resources' and direction == 'asc' else 'asc' }}">Ressources</a></th>
                    <th><a href="?sort_by=complexity&direction={{ 'desc' if sort_by == 'complexity' and direction == 'asc' else 'asc' }}">Complexité</a></th>
                    <th><a href="?sort_by=alignment&direction={{ 'desc' if sort_by == 'alignment' and direction == 'asc' else 'asc' }}">Alignement</a></th>
                    <th><a href="?sort_by=due_date&direction={{ 'desc' if sort_by == 'due_date' and direction == 'asc' else 'asc' }}">Date d'échéance</a></th>
                    <th><a href="?sort_by=planned_date&direction={{ 'desc' if sort_by == 'planned_date' and direction == 'asc' else 'asc' }}">Date de réalisation</a></th>
                    <th><a href="?sort_by=recurrence&direction={{ 'desc' if sort_by == 'recurrence' and direction == 'asc' else 'asc' }}">Récurrence</a></th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for task in daily_tasks if task.is_done %}
                <tr>
                    <td>{{ task.name }}</td>
                    <td>{{ task.project.name if task.project else "Indépendant" }}</td>
                    <td>{{ "%.2f"|format(task.priority) }}%</td>
                    <td>{{ "%.2f"|format(task.urgency) }}%</td>
                    <td>{{ "%.2f"|format(task.impact) }}%</td>
                    <td>{{ "%.2f"|format(task.resources) }}%</td>
                    <td>{{ "%.2f"|format(task.complexity) }}%</td>
                    <td>{{ "%.2f"|format(task.alignment) }}%</td>
                    <td>{{ task.due_date if task.due_date else "Aucune" }}</td>
                    <td>{{ task.planned_date if task.planned_date else "Aucune" }}</td>
                    <td>{{ task.recurrence if task.recurrence else "Aucune" }}</td>
                    <td>
                        <a href="{{ url_for('mark_task_undone', id=task.id) }}">Non fait ?</a>
                        <a href="/tasks/{{ task.id }}/details">Détails</a>
                        <a href="/tasks/{{ task.id }}/edit">Modifier</a>
                        <form action="{{ url_for('delete_task', id=task.id) }}" method="post" style="display:inline;">
                            <button type="submit">Supprimer</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <h2>Créer une nouvelle tâche</h2>
        <form action="{{ url_for('create_task') }}" method="post">
            <input type="text" name="name" placeholder="Nom de la tâche" required>
            <input type="hidden" name="planned_date" value="{{ today }}">
            <button type="submit">Créer la tâche</button>
        </form>
    </div>
</body>
</html>
