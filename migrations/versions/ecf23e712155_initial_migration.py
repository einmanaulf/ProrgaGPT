"""Initial migration

Revision ID: ecf23e712155
Revises: 
Create Date: 2024-05-24 15:00:56.496853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecf23e712155'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('due_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('planned_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('urgency', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('impact', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('resources', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('complexity', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('alignment', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recurrence', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('order')
        batch_op.drop_column('recurrence')
        batch_op.drop_column('alignment')
        batch_op.drop_column('complexity')
        batch_op.drop_column('resources')
        batch_op.drop_column('impact')
        batch_op.drop_column('urgency')
        batch_op.drop_column('planned_date')
        batch_op.drop_column('due_date')

    # ### end Alembic commands ###