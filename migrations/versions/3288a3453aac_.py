"""empty message

Revision ID: 3288a3453aac
Revises: 182ab0f80acb
Create Date: 2025-03-25 11:41:25.722068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3288a3453aac'
down_revision = '182ab0f80acb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invoice',
    sa.Column('invoice_number', sa.Integer(), nullable=False),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_status', sa.String(), nullable=True),
    sa.Column('registration_total', sa.Integer(), nullable=True),
    sa.Column('nmr_total', sa.Integer(), nullable=True),
    sa.Column('donation_total', sa.Integer(), nullable=True),
    sa.Column('invoice_total', sa.Integer(), sa.Computed('registration_total + nmr_total + donation_total', ), nullable=True),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('invoice_number')
    )
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('invoice_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('payment_regs_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'invoice', ['invoice_id'], ['invoice_number'])
        batch_op.drop_column('regs')

    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('invoice_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'invoice', ['invoice_id'], ['invoice_number'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('invoice_id')

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('regs', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('payment_regs_fkey', 'registrations', ['regs'], ['id'])
        batch_op.drop_column('invoice_id')

    op.drop_table('invoice')
    # ### end Alembic commands ###
