"""empty message

Revision ID: a572a9403f31
Revises: 6e2e2543b947
Create Date: 2024-06-24 19:24:04.153355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a572a9403f31'
down_revision = '6e2e2543b947'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bow_inspection_martial_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('bow_inspection_date', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['bow_inspection_martial_id'], ['id'])

    with op.batch_alter_table('crossbows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('crossbow_inspection_martial_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('crossbow_inspection_date', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['crossbow_inspection_martial_id'], ['id'])

    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.alter_column('chivalric_inspection_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)
        batch_op.alter_column('rapier_inspection_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.alter_column('rapier_inspection_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('chivalric_inspection_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)

    with op.batch_alter_table('crossbows', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('crossbow_inspection_date')
        batch_op.drop_column('crossbow_inspection_martial_id')

    with op.batch_alter_table('bows', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('bow_inspection_date')
        batch_op.drop_column('bow_inspection_martial_id')

    # ### end Alembic commands ###

