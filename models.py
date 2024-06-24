from app import db
from datetime import date

# Associations Tables
task_material_association = db.Table('task_material_association',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('material_id', db.Integer, db.ForeignKey('material.id'))
)

task_protection_association = db.Table('task_protection_association',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('protection_id', db.Integer, db.ForeignKey('protection.id'))
)

task_consumable_association = db.Table('task_consumable_association',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('consumable_id', db.Integer, db.ForeignKey('consumable.id'))
)

task_task_association = db.Table('task_task_association',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('prerequisite_task_id', db.Integer, db.ForeignKey('task.id'))
)

task_project_association = db.Table('task_project_association',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)

project_protection_association = db.Table('project_protection_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('protection_id', db.Integer, db.ForeignKey('protection.id'))
)

project_material_association = db.Table('project_material_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('material_id', db.Integer, db.ForeignKey('material.id'))
)

project_consumable_association = db.Table('project_consumable_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('consumable_id', db.Integer, db.ForeignKey('consumable.id'))
)

project_project_association = db.Table('project_project_association',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('prerequisite_project_id', db.Integer, db.ForeignKey('project.id'))
)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True, default=None)
    planned_date = db.Column(db.Date, nullable=True, default=None)
    recurrence = db.Column(db.String(100), nullable=True, default=0)
    time_required = db.Column(db.Float, nullable=True, default=0)
    time_required_unit = db.Column(db.String(20), nullable=True, default='seconds')
    funding = db.Column(db.Float, nullable=True, default=0)
    benefits = db.Column(db.Float, nullable=True, default=0)
    time_to_sell = db.Column(db.Float, nullable=True, default=0)
    time_to_sell_unit = db.Column(db.String(20), nullable=True, default='seconds')

    # Priority attributes
    urgency = db.Column(db.Float, default=0.0)
    impact = db.Column(db.Float, default=0.0)
    resources = db.Column(db.Float, default=0.0)
    complexity = db.Column(db.Float, default=0.0)
    alignment = db.Column(db.Float, default=0.0)
    priority = db.Column(db.Float, default=0.0)
    order = db.Column(db.Integer, nullable=True, default=None)
    is_daily = db.Column(db.Boolean, default=False)

    materials = db.relationship('Material', secondary=task_material_association, back_populates='tasks')
    consumables = db.relationship('Consumable', secondary=task_consumable_association, back_populates='tasks')
    protections = db.relationship('Protection', secondary=task_protection_association, back_populates='tasks')

    prerequisites = db.relationship(
        'Task', secondary=task_task_association,
        primaryjoin=id == task_task_association.c.task_id,
        secondaryjoin=id == task_task_association.c.prerequisite_task_id,
        backref='dependent_tasks',
        overlaps="dependent_tasks,prerequisite_projects"
    )

    prerequisite_projects = db.relationship(
        'Project', secondary=task_project_association,
        primaryjoin=id == task_project_association.c.task_id,
        secondaryjoin=id == task_project_association.c.project_id,
        backref='tasks_requiring_this_project',
        overlaps="dependent_projects,prerequisite_tasks"
    )

    dependent_projects = db.relationship(
        'Project', secondary=task_project_association,
        primaryjoin=id == task_project_association.c.task_id,
        secondaryjoin=id == task_project_association.c.project_id,
        overlaps="tasks_requiring_this_project"
    )

    def __init__(self, name, project_id=None, is_done=False, due_date=None, planned_date=None, recurrence=0, time_required=0,
                 time_required_unit='seconds', funding=0, benefits=0, time_to_sell=0, time_to_sell_unit='seconds', urgency=0,
                 impact=0, resources=0, complexity=0, alignment=0, order=None):
        self.name = name
        self.project_id = project_id
        self.is_done = is_done
        self.due_date = due_date
        self.planned_date = planned_date
        self.recurrence = recurrence
        self.time_required = time_required
        self.time_required_unit = time_required_unit
        self.funding = funding
        self.benefits = benefits
        self.time_to_sell = time_to_sell
        self.time_to_sell_unit = time_to_sell_unit
        self.urgency = urgency
        self.impact = impact
        self.resources = resources
        self.complexity = complexity
        self.alignment = alignment
        self.order = order
        self.is_daily = self.check_if_daily()

    def check_if_daily(self):
        today = date.today()
        return (self.due_date and self.due_date >= today) or (self.planned_date and self.planned_date >= today)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text, default='')
    principle = db.Column(db.Text, default='')
    protocol = db.Column(db.Text, default='')
    time_required = db.Column(db.String(50), default='0')
    time_required_unit = db.Column(db.String(20), default='seconds')
    funding = db.Column(db.Float, default=0.0)
    benefits = db.Column(db.Float, nullable=True, default=0)
    time_to_sell = db.Column(db.String(50), default='0')
    time_to_sell_unit = db.Column(db.String(20), default='seconds')
    due_date = db.Column(db.Date, nullable=True, default=None)
    planned_date = db.Column(db.Date, nullable=True, default=None)

    # Priority attributes
    urgency = db.Column(db.Float, default=0.0)
    impact = db.Column(db.Float, default=0.0)
    resources = db.Column(db.Float, default=0.0)
    complexity = db.Column(db.Float, default=0.0)
    alignment = db.Column(db.Float, default=0.0)
    priority = db.Column(db.Float, default=0.0)

    protections = db.relationship('Protection', secondary=project_protection_association, back_populates='projects')
    materials = db.relationship('Material', secondary=project_material_association, back_populates='projects')
    consumables = db.relationship('Consumable', secondary=project_consumable_association, back_populates='projects')

    prerequisites = db.relationship(
        'Project', secondary=project_project_association,
        primaryjoin=id == project_project_association.c.project_id,
        secondaryjoin=id == project_project_association.c.prerequisite_project_id,
        backref='dependent_projects',
        overlaps="prerequisite_projects"
    )

    prerequisite_tasks = db.relationship(
        'Task', secondary=task_project_association,
        primaryjoin=id == task_project_association.c.project_id,
        secondaryjoin=id == task_project_association.c.task_id,
        backref='projects_requiring_this_task',
        overlaps="dependent_tasks,prerequisite_projects"
    )

    dependent_tasks = db.relationship(
        'Task', secondary=task_project_association,
        primaryjoin=id == task_project_association.c.project_id,
        secondaryjoin=id == task_project_association.c.task_id,
        overlaps="projects_requiring_this_task"
    )

    tasks = db.relationship('Task', backref='project', lazy=True)
    def __init__(self, name, goal='', principle='', protocol='', time_required='0', time_required_unit='seconds', funding=0.0, benefits=0, time_to_sell='0', time_to_sell_unit='seconds', due_date=None, planned_date=None):
        self.name = name
        self.goal = goal
        self.principle = principle
        self.protocol = protocol
        self.time_required = time_required
        self.time_required_unit = time_required_unit
        self.funding = funding
        self.benefits = benefits
        self.time_to_sell = time_to_sell
        self.time_to_sell_unit = time_to_sell_unit
        self.due_date = due_date
        self.planned_date = planned_date

    def __repr__(self):
        return f'<Project {self.name}>'



class Protection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=True, default=0)
    tasks = db.relationship('Task', secondary=task_protection_association, back_populates='protections')
    projects = db.relationship('Project', secondary=project_protection_association, back_populates='protections')

    def __init__(self, name, quantity=None):
        self.name = name
        self.quantity = quantity if quantity is not None else 0

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=True, default=0)
    tasks = db.relationship('Task', secondary=task_material_association, back_populates='materials')
    projects = db.relationship('Project', secondary=project_material_association, back_populates='materials')

    def __init__(self, name, quantity=None):
        self.name = name
        self.quantity = quantity if quantity is not None else 0

class Consumable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=True, default=0)
    tasks = db.relationship('Task', secondary=task_consumable_association, back_populates='consumables')
    projects = db.relationship('Project', secondary=project_consumable_association, back_populates='consumables')

    def __init__(self, name, quantity=None):
        self.name = name
        self.quantity = quantity if quantity is not None else 0

class Funds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)


class TaskResource(db.Model):
    __tablename__ = 'task_resources'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    resource_id = db.Column(db.Integer)
    resource_type = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=True, default=1)

    task = db.relationship('Task', backref=db.backref('task_resources', cascade='all, delete-orphan'))

    @property
    def material(self):
        return Material.query.get(self.resource_id)

    @property
    def consumable(self):
        return Consumable.query.get(self.resource_id)

    @property
    def protection(self):
        return Protection.query.get(self.resource_id)
class TaskPrerequisite(db.Model):
    __tablename__ = 'task_prerequisites'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    prerequisite_id = db.Column(db.Integer)
    prerequisite_type = db.Column(db.String(50))

    task = db.relationship('Task', backref=db.backref('task_prerequisites', cascade='all, delete-orphan'))


class ProjectResource(db.Model):
    __tablename__ = 'project_resources'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    resource_id = db.Column(db.Integer)
    resource_type = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=True, default=1)

    project = db.relationship('Project', backref=db.backref('project_resources', cascade='all, delete-orphan'))

    @property
    def material(self):
        return Material.query.get(self.resource_id)

    @property
    def consumable(self):
        return Consumable.query.get(self.resource_id)

    @property
    def protection(self):
        return Protection.query.get(self.resource_id)
print("Models importé")
