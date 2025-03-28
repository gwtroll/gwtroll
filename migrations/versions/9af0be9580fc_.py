"""empty message

Revision ID: 9af0be9580fc
Revises: c843c45d8f79
Create Date: 2025-03-27 17:21:31.876597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9af0be9580fc'
down_revision = 'c843c45d8f79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registration_amount', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nmr_amount', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('paypal_donation_amount', sa.Integer(), nullable=True))

    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registration_balance', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nmr_balance', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('paypal_donation_balance', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('paypal_donation_balance')
        batch_op.drop_column('nmr_balance')
        batch_op.drop_column('registration_balance')

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('paypal_donation_amount')
        batch_op.drop_column('nmr_amount')
        batch_op.drop_column('registration_amount')

    # ### end Alembic commands ###
