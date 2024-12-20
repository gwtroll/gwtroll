"""empty message

Revision ID: a60488369757
Revises: eae95cda177f
Create Date: 2024-10-17 09:17:33.731501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a60488369757'
down_revision = 'eae95cda177f'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('adult', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('prereg_date_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_registrations_prereg_date_time'))
        batch_op.drop_column('prereg_date_time')
        batch_op.drop_column('adult')

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
    # ### end Alembic commands ###

