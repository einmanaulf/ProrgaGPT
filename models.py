from sqlalchemy import Table, Column, Integer, ForeignKey, String, Float, Date, Boolean, Text
from sqlalchemy.orm import relationship
from app import db
from datetime import datetime

# Association Tables
task_task_association = Table('task_task_association', db.Model.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('prerequisite_task_id', Integer, ForeignKey('tasks.id'), primary_key=True)
)
task_material_association = Table('task_material_association', db.Model.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('material_id', Integer, ForeignKey('materials.id'), primary_key=True)
)

task_protection_association = Table('task_protection_association', db.Model.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('protection_id', Integer, ForeignKey('protections.id'), primary_key=True)
)

task_consumable_association = Table('task_consumable_association', db.Model.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('consumable_id', Integer, ForeignKey('consumables.id'), primary_key=True)
)
project_protection_association = Table('project_protection_association', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('protection_id', Integer, ForeignKey('protections.id'), primary_key=True)
)

project_material_association = Table('project_material_association', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('material_id', Integer, ForeignKey('materials.id'), primary_key=True)
)

project_consumable_association = Table('project_consumable_association', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('consumable_id', Integer, ForeignKey('consumables.id'), primary_key=True)
)

project_project_association = Table('project_project_association', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('prerequisite_project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)

protocol_protection_association = Table('protocol_protection_association', db.Model.metadata,
    Column('protocol_id', Integer, ForeignKey('protocols.id')),
    Column('protection_id', Integer, ForeignKey('protections.id')),
    extend_existing=True
)

protocol_material_association = Table('protocol_material_association', db.Model.metadata,
    Column('protocol_id', Integer, ForeignKey('protocols.id')),
    Column('material_id', Integer, ForeignKey('materials.id')),
    extend_existing=True
)

protocol_consumable_association = Table('protocol_consumable_association', db.Model.metadata,
    Column('protocol_id', Integer, ForeignKey('protocols.id')),
    Column('consumable_id', Integer, ForeignKey('consumables.id')),
    extend_existing=True
)

protocol_protocol_association = Table('protocol_protocol_association', db.Model.metadata,
    Column('protocol_id', Integer, ForeignKey('protocols.id'), primary_key=True),
    Column('prerequisite_protocol_id', Integer, ForeignKey('protocols.id'), primary_key=True)
)
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def generate_identifier(self, prefix):
        last_item = self.query.order_by(self.id.desc()).first()
        number = last_item.id + 1 if last_item else 1
        date_str = self.last_modified.strftime('%d-%m-%Y-%H%M')
        self.identifier = f"{prefix}{number}_{date_str}"

    def save(self, prefix):
        if not self.identifier:
            self.generate_identifier(prefix)
        self.last_modified = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

class BaseActivity(BaseModel):
    __abstract__ = True
    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text, default='')
    principle = db.Column(db.Text, default='')
    protocol_text = db.Column(db.Text, default='')
    time_required = db.Column(db.Float, nullable=True, default=0)
    time_required_unit = db.Column(db.String(20), nullable=True, default='seconds')
    funding = db.Column(db.Float, nullable=True, default=0)
    benefits = db.Column(db.Float, nullable=True, default=0)
    time_to_sell = db.Column(db.Float, nullable=True, default=0)
    time_to_sell_unit = db.Column(db.String(20), nullable=True, default='seconds')

class Task(BaseActivity):
    __tablename__ = 'tasks'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    project = db.relationship('Project', backref=db.backref('tasks', lazy=True))
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'), nullable=True)
    protocol = db.relationship('Protocol', backref=db.backref('tasks', lazy=True))
    is_done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True, default=None)
    planned_date = db.Column(db.Date, nullable=True, default=None)
    recurrence = db.Column(db.String(100), nullable=True, default='0')
    urgency = db.Column(db.Float, default=0.0)
    impact = db.Column(db.Float, default=0.0)
    resources = db.Column(db.Float, default=0.0)
    complexity = db.Column(db.Float, default=0.0)
    alignment = db.Column(db.Float, default=0.0)
    priority = db.Column(db.Float, default=0.0)
    order = db.Column(db.Integer, nullable=True, default=None)
    is_daily = db.Column(db.Boolean, default=False)
    prerequisites = db.relationship(
        'Task', secondary=task_task_association,
        primaryjoin=id == task_task_association.c.task_id,
        secondaryjoin=id == task_task_association.c.prerequisite_task_id,
        backref=db.backref('dependent_tasks', lazy='dynamic'),
        remote_side=[task_task_association.c.prerequisite_task_id]
    )

    def __init__(self, name, project_id=None, protocol_id=None, is_done=False, due_date=None, planned_date=None,
                 recurrence='0', urgency=0.0, impact=0.0, resources=0.0, complexity=0.0, alignment=0.0, priority=0.0, order=None, **kwargs):
        super().__init__(name, **kwargs)
        self.project_id = project_id
        self.protocol_id = protocol_id
        self.is_done = is_done
        self.due_date = due_date
        self.planned_date = planned_date
        self.recurrence = recurrence
        self.urgency = urgency
        self.impact = impact
        self.resources = resources
        self.complexity = complexity
        self.alignment = alignment
        self.priority = priority
        self.order = order
        self.is_daily = self.check_if_daily()
        self.save('T')

    def check_if_daily(self):
        today = datetime.today().date()
        return (self.due_date and self.due_date >= today) or (self.planned_date and self.planned_date >= today)

class Project(BaseActivity):
    __tablename__ = 'projects'
    due_date = db.Column(db.Date, nullable=True, default=None)
    planned_date = db.Column(db.Date, nullable=True, default=None)
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
        primaryjoin=(project_project_association.c.project_id == id),
        secondaryjoin=(project_project_association.c.prerequisite_project_id == id),
        backref=db.backref('dependent_projects', lazy='dynamic'),
        remote_side=[project_project_association.c.prerequisite_project_id]
    )

    def __init__(self, name, due_date=None, planned_date=None, urgency=0.0, impact=0.0, resources=0.0, complexity=0.0, alignment=0.0, priority=0.0, **kwargs):
        super().__init__(name, **kwargs)
        self.due_date = due_date
        self.planned_date = planned_date
        self.urgency = urgency
        self.impact = impact
        self.resources = resources
        self.complexity = complexity
        self.alignment = alignment
        self.priority = priority
        self.save('Pj')

    def __repr__(self):
        return f'<Project {self.name}>'

class Protocol(BaseActivity):
    __tablename__ = 'protocols'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    project = db.relationship('Project', backref=db.backref('protocols', lazy=True))
    protections = db.relationship('Protection', secondary=protocol_protection_association, back_populates='protocols')
    materials = db.relationship('Material', secondary=protocol_material_association, back_populates='protocols')
    consumables = db.relationship('Consumable', secondary=protocol_consumable_association, back_populates='protocols')
    prerequisites = db.relationship(
        'Protocol', secondary=protocol_protocol_association,
        primaryjoin=(protocol_protocol_association.c.protocol_id == id),
        secondaryjoin=(protocol_protocol_association.c.prerequisite_protocol_id == id),
        backref=db.backref('dependent_protocols', lazy='dynamic'),
        remote_side=[protocol_protocol_association.c.prerequisite_protocol_id]
    )

    def __init__(self, name, project_id=None, **kwargs):
        super().__init__(name, **kwargs)
        self.project_id = project_id
        self.save('Pt')

    def __repr__(self):
        return f'<Protocol {self.name}>'

#Ressouces
class BaseResource(BaseModel):
    __abstract__ = True
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=True, default=0)

    def __init__(self, name, quantity=None):
        self.name = name
        self.quantity = quantity if quantity is not None else 0
        super().__init__()

    def save(self):
        self.last_modified = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

class TaskResource(db.Model):
    __tablename__ = 'task_resources'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
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
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    prerequisite_type = db.Column(db.String(50))

    task = db.relationship('Task', foreign_keys=[task_id], backref=db.backref('task_prerequisites', cascade='all, delete-orphan'))
    prerequisite = db.relationship('Task', foreign_keys=[prerequisite_id])

class ProjectResource(db.Model):
    __tablename__ = 'project_resources'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
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

class ProjectPrerequisite(db.Model):
    __tablename__ = 'project_prerequisites'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    prerequisite_id = db.Column(db.Integer)
    prerequisite_type = db.Column(db.String(50))

    project = db.relationship('Project', backref=db.backref('project_prerequisites', cascade='all, delete-orphan'))

class ProtocolResource(db.Model):
    __tablename__ = 'protocol_resources'
    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'))
    resource_id = db.Column(db.Integer)
    resource_type = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=True, default=1)

    project = db.relationship('Protocol', backref=db.backref('protocol_resources', cascade='all, delete-orphan'))

    @property
    def material(self):
        return Material.query.get(self.resource_id)

    @property
    def consumable(self):
        return Consumable.query.get(self.resource_id)

    @property
    def protection(self):
        return Protection.query.get(self.resource_id)

class ProtocolPrerequisite(db.Model):
    __tablename__ = 'protocol_prerequisites'
    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'))
    prerequisite_id = db.Column(db.Integer)
    prerequisite_type = db.Column(db.String(50))

    protocol = db.relationship('Protocol', backref=db.backref('protocol_prerequisites', cascade='all, delete-orphan'))


#PROTECTIONS
class Protection(BaseResource):
    __tablename__ = 'protections'
    tasks = db.relationship('Task', secondary=task_protection_association, back_populates='protections')
    projects = db.relationship('Project', secondary=project_protection_association, back_populates='protections')
    protocols = db.relationship('Protocol', secondary=protocol_protection_association, back_populates='protections')

    def __init__(self, name, quantity=None):
        super().__init__(name, quantity)

#MATERIALS
class Material(BaseResource):
    __tablename__ = 'materials'
    tasks = db.relationship('Task', secondary=task_material_association, back_populates='materials')
    projects = db.relationship('Project', secondary=project_material_association, back_populates='materials')
    protocols = db.relationship('Protocol', secondary=protocol_material_association, back_populates='materials')

    def __init__(self, name, quantity=None):
        super().__init__(name, quantity)

#CONSUMABLES
class Consumable(BaseResource):
    __tablename__ = 'consumables'
    tasks = db.relationship('Task', secondary=task_consumable_association, back_populates='consumables')
    projects = db.relationship('Project', secondary=project_consumable_association, back_populates='consumables')
    protocols = db.relationship('Protocol', secondary=protocol_consumable_association, back_populates='consumables')

    def __init__(self, name, quantity=None):
        super().__init__(name, quantity)

#FUNDS
class Funds(BaseModel):
    __tablename__ = 'funds'
    name = db.Column(db.String(100), nullable=False)  # Ajouter cette ligne
    amount = db.Column(db.Float, nullable=False)

    def __init__(self, name, amount):
        self.name = name  # Ajouter cette ligne
        self.amount = amount
        super().__init__()  # Corriger cette ligne
print("Models importé")
