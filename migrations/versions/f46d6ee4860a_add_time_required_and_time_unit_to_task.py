"""Add time_required and time_unit to Task

Revision ID: f46d6ee4860a
Revises: ed2460bc8014
Create Date: 2024-05-24 22:21:11.653644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f46d6ee4860a'
down_revision = 'ed2460bc8014'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.alter_column('time',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('funding',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('urgency',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('impact',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('resources',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('complexity',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('alignment',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_required', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('time_unit', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('funding', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('benefits', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('time_to_sell', sa.Float(), nullable=True))
        batch_op.alter_column('urgency',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('impact',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('resources',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('complexity',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('alignment',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('recurrence',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.alter_column('recurrence',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
        batch_op.alter_column('alignment',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('complexity',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('resources',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('impact',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('urgency',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.drop_column('time_to_sell')
        batch_op.drop_column('benefits')
        batch_op.drop_column('funding')
        batch_op.drop_column('time_unit')
        batch_op.drop_column('time_required')

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.alter_column('alignment',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('complexity',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('resources',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('impact',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('urgency',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('funding',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('time',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###