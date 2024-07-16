from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Table d'association
task_task_association = Table('task_task_association', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('prerequisite_task_id', Integer, ForeignKey('tasks.id'))
)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    prerequisites = relationship(
        'Task', secondary=task_task_association,
        primaryjoin=(task_task_association.c.task_id == id),
        secondaryjoin=(task_task_association.c.prerequisite_task_id == id),
        backref='dependent_tasks',
        sync_backref=False,
        remote_side=[task_task_association.c.prerequisite_task_id]
    )

# Définition de la base de données et des sessions
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
