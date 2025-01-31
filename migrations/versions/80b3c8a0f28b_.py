"""empty message

Revision ID: 80b3c8a0f28b
Revises: 
Create Date: 2025-01-28 14:42:52.335386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80b3c8a0f28b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('poundage', sa.Double(), nullable=True),
    sa.Column('bow_inspection_martial_id', sa.Integer(), nullable=True),
    sa.Column('bow_inspection_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['bow_inspection_martial_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crossbows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inchpounds', sa.Double(), nullable=True),
    sa.Column('crossbow_inspection_martial_id', sa.Integer(), nullable=True),
    sa.Column('crossbow_inspection_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['crossbow_inspection_martial_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reg_bows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('regid', sa.Integer(), nullable=True),
    sa.Column('bowid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bowid'], ['bows.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regid'], ['registrations.regid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reg_crossbows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('regid', sa.Integer(), nullable=True),
    sa.Column('crossbowid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['crossbowid'], ['crossbows.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regid'], ['registrations.regid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('chivalric_inspection_martial_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rapier_inspection_martial_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('chivalric_inspection', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('chivalric_inspection_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('rapier_inspection', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('rapier_inspection_date', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['chivalric_inspection_martial_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['rapier_inspection_martial_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('rapier_inspection_date')
        batch_op.drop_column('rapier_inspection')
        batch_op.drop_column('chivalric_inspection_date')
        batch_op.drop_column('chivalric_inspection')
        batch_op.drop_column('rapier_inspection_martial_id')
        batch_op.drop_column('chivalric_inspection_martial_id')

    op.drop_table('reg_crossbows')
    op.drop_table('reg_bows')
    op.drop_table('crossbows')
    op.drop_table('bows')
    # ### end Alembic commands ###
