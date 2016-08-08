"""empty message

Revision ID: 52c5946188c4
Revises: 410f1493e84b
Create Date: 2016-08-08 12:40:51.950670

"""

# revision identifiers, used by Alembic.
revision = '52c5946188c4'
down_revision = '410f1493e84b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade_():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def upgrade_stats():
    import os
    if os.environ.get("SPLICE_IGNORE_REDSHIFT", "") == "true":
        return
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity_stream_events_daily', sa.Column('highlight_type', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade_stats():
    import os
    if os.environ.get("SPLICE_IGNORE_REDSHIFT", "") == "true":
        return
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activity_stream_events_daily', 'highlight_type')
    ### end Alembic commands ###

