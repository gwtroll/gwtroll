"""registrations table

Revision ID: df2868f70f10
Revises: 752d7e7f9d18
Create Date: 2024-03-08 01:24:08.393579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df2868f70f10'
down_revision = '752d7e7f9d18'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.alter_column('scaname',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.alter_column('scaname',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)

    # ### end Alembic commands ###
