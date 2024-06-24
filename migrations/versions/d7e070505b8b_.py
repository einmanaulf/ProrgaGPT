"""empty message

Revision ID: d7e070505b8b
Revises: ea8533f466f0
Create Date: 2024-05-31 21:12:18.157142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e070505b8b'
down_revision = 'ea8533f466f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_prerequisite_association',
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('prerequisite_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['prerequisite_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], )
    )
    op.drop_table('project_project_association')
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('urgency', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('impact', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('resources', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('complexity', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('alignment', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.Float(), nullable=True))

    with op.batch_alter_table('task_consumable_association', schema=None) as batch_op:
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('consumable_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('task_protection_association', schema=None) as batch_op:
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('protection_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_protection_association', schema=None) as batch_op:
        batch_op.alter_column('protection_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('task_consumable_association', schema=None) as batch_op:
        batch_op.alter_column('consumable_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('priority')
        batch_op.drop_column('alignment')
        batch_op.drop_column('complexity')
        batch_op.drop_column('resources')
        batch_op.drop_column('impact')
        batch_op.drop_column('urgency')

    op.create_table('project_project_association',
    sa.Column('project_id', sa.INTEGER(), nullable=True),
    sa.Column('prerequisite_project_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['prerequisite_project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], )
    )
    op.drop_table('project_prerequisite_association')
    # ### end Alembic commands ###