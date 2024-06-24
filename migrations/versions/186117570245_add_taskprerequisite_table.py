"""Add TaskPrerequisite table

Revision ID: 186117570245
Revises: a8281b2efdef
Create Date: 2024-06-24 18:12:36.479229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '186117570245'
down_revision = 'a8281b2efdef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_prerequisites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('prerequisite_id', sa.Integer(), nullable=True),
    sa.Column('prerequisite_type', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_prerequisites')
    # ### end Alembic commands ###
