"""empty message

Revision ID: 29166b03d02a
Revises: 38617ef830fc
Create Date: 2014-09-12 10:49:37.518724

"""

# revision identifiers, used by Alembic.
revision = '29166b03d02a'
down_revision = '38617ef830fc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('distributions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('distributions')
    ### end Alembic commands ###
