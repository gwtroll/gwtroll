"""empty message

Revision ID: 0a84fa06f43d
Revises: 89189f9c7c50
Create Date: 2024-10-28 13:08:41.429378

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0a84fa06f43d'
down_revision = '89189f9c7c50'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('invoice_status', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('invoice_status')

    op.create_table('reg_crossbows',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('regid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('crossbowid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['crossbowid'], ['crossbows.id'], name='reg_crossbows_crossbowid_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regid'], ['registrations.regid'], name='reg_crossbows_regid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='reg_crossbows_pkey')
    )
    op.create_table('crossbows',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('inchpounds', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('crossbow_inspection_martial_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('crossbow_inspection_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['crossbow_inspection_martial_id'], ['users.id'], name='crossbows_crossbow_inspection_martial_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='crossbows_pkey')
    )
    op.create_table('bows',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('bows_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('poundage', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('bow_inspection_martial_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('bow_inspection_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['bow_inspection_martial_id'], ['users.id'], name='bows_bow_inspection_martial_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='bows_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('reg_bows',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('regid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('bowid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['bowid'], ['bows.id'], name='reg_bows_bowid_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regid'], ['registrations.regid'], name='reg_bows_regid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='reg_bows_pkey')
    )
    # ### end Alembic commands ###

