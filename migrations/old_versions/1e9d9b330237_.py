"""empty message

Revision ID: 1e9d9b330237
Revises: 37a805fca5aa
Create Date: 2015-05-25 17:29:19.372529

"""

# revision identifiers, used by Alembic.
revision = '1e9d9b330237'
down_revision = '37a805fca5aa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('adgroups', sa.Column('end_date', sa.String(length=30), nullable=True))
    op.add_column('adgroups', sa.Column('end_date_dt', sa.DateTime(), nullable=True))
    op.add_column('adgroups', sa.Column('start_date', sa.String(length=30), nullable=True))
    op.add_column('adgroups', sa.Column('start_date_dt', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('adgroups', 'start_date_dt')
    op.drop_column('adgroups', 'start_date')
    op.drop_column('adgroups', 'end_date_dt')
    op.drop_column('adgroups', 'end_date')
    ### end Alembic commands ###