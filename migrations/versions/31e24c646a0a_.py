"""empty message

Revision ID: 31e24c646a0a
Revises: 11b247298da4
Create Date: 2016-05-26 15:48:09.610444

"""

# revision identifiers, used by Alembic.
revision = '31e24c646a0a'
down_revision = '11b247298da4'
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
    op.create_table('activity_stream_performance_daily',
    sa.Column('client_id', sa.String(length=64), nullable=False),
    sa.Column('tab_id', sa.String(length=64), nullable=False),
    sa.Column('addon_version', sa.String(length=64), nullable=False),
    sa.Column('source', sa.String(length=64), nullable=False),
    sa.Column('session_id', sa.String(length=64), nullable=True),
    sa.Column('experiment_id', sa.String(length=64), nullable=True),
    sa.Column('event', sa.String(length=64), nullable=False),
    sa.Column('event_id', sa.String(length=64), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('receive_at', sa.DateTime(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('locale', sa.String(length=14), nullable=False),
    sa.Column('country_code', sa.String(length=5), nullable=False),
    sa.Column('os', sa.String(length=64), nullable=False),
    sa.Column('browser', sa.String(length=64), nullable=False),
    sa.Column('version', sa.String(length=64), nullable=False),
    sa.Column('device', sa.String(length=64), nullable=False)
    )
    op.add_column(u'activity_stream_events_daily', sa.Column('session_id', sa.String(length=64), nullable=True))
    op.add_column('activity_stream_events_daily', sa.Column('experiment_id', sa.String(length=64), nullable=True))
    op.add_column(u'activity_stream_stats_daily', sa.Column('session_id', sa.String(length=64), nullable=True))
    op.add_column('activity_stream_stats_daily', sa.Column('experiment_id', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade_stats():
    import os
    if os.environ.get("SPLICE_IGNORE_REDSHIFT", "") == "true":
        return
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('activity_stream_performance_daily')
    op.drop_column(u'activity_stream_stats_daily', 'session_id')
    op.drop_column('activity_stream_stats_daily', 'experiment_id')
    op.drop_column(u'activity_stream_events_daily', 'session_id')
    op.drop_column('activity_stream_events_daily', 'experiment_id')
    ### end Alembic commands ###