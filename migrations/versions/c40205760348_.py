"""empty message

Revision ID: c40205760348
Revises: 88e329d04ba6
Create Date: 2025-03-24 14:40:02.438338

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c40205760348'
down_revision = '88e329d04ba6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('payment_date', sa.DateTime(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('invoice')
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('mbr', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('prereg', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('expected_arrival_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('registration_price', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nmr_price', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('actual_arrival_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('invoice_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('invoice_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('invoice_status', sa.String(), nullable=True))
        batch_op.alter_column('paypal_donation',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True,
               postgresql_using='paypal_donation::int')
        batch_op.add_column(sa.Column('total_due', sa.Integer(), sa.Computed('registration_price + nmr_price + paypal_donation', ), nullable=True))
        batch_op.drop_column('price_calc')
        batch_op.drop_column('price_due')
        batch_op.drop_column('rate_age')
        batch_op.drop_column('event_ticket')
        batch_op.drop_column('prereg_status')
        batch_op.drop_column('pay_type')
        batch_op.drop_column('atd_pay_type')
        batch_op.drop_column('rate_mbr')
        batch_op.drop_column('rate_date')
        batch_op.drop_column('atd_paid')
        batch_op.drop_column('paypal_donation_amount')
        batch_op.drop_column('price_paid')
        batch_op.drop_column('requests')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requests', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('price_paid', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('paypal_donation_amount', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('atd_paid', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('rate_date', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('rate_mbr', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('atd_pay_type', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('pay_type', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('prereg_status', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('event_ticket', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('rate_age', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('price_due', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('price_calc', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.alter_column('paypal_donation',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('total_due')
        batch_op.drop_column('invoice_status')
        batch_op.drop_column('invoice_date')
        batch_op.drop_column('invoice_number')
        batch_op.drop_column('actual_arrival_date')
        batch_op.drop_column('nmr_price')
        batch_op.drop_column('registration_price')
        batch_op.drop_column('expected_arrival_date')
        batch_op.drop_column('prereg')
        batch_op.drop_column('mbr')
        batch_op.drop_column('age')

    op.create_table('invoice',
    sa.Column('invoice_number', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('invoice_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('invoice_payment_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('invoice_status', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('invoice_number', name='invoice_pkey')
    )
    op.drop_table('payment')
    # ### end Alembic commands ###
