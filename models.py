from app import db

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
