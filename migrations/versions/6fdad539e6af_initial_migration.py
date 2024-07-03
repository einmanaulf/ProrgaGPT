"""Initial migration.

Revision ID: 6fdad539e6af
Revises: 186117570245
Create Date: 2024-06-24 23:13:55.994190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fdad539e6af'
down_revision = '186117570245'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_project_association',
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('prerequisite_project_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['prerequisite_project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], )
    )
    op.create_table('task_project_association',
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], )
    )
    op.drop_table('project_prerequisite_association')
    with op.batch_alter_table('task_consumable_association', schema=None) as batch_op:
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('consumable_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('task_protection_association', schema=None) as batch_op:
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('protection_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_protection_association', schema=None) as batch_op:
        batch_op.alter_column('protection_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('task_consumable_association', schema=None) as batch_op:
        batch_op.alter_column('consumable_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    op.create_table('project_prerequisite_association',
    sa.Column('project_id', sa.INTEGER(), nullable=True),
    sa.Column('prerequisite_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['prerequisite_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], )
    )
    op.drop_table('task_project_association')
    op.drop_table('project_project_association')
    # ### end Alembic commands ###
