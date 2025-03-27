"""empty message

Revision ID: df918678f5c0
Revises: e543ea1054d9
Create Date: 2025-03-26 09:52:33.608049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df918678f5c0'
down_revision = 'e543ea1054d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('balance', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('balance')

    # ### end Alembic commands ###
