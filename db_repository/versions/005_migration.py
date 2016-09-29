from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
opponents = Table('opponents', pre_meta,
    Column('game_id', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('opponent1_id', INTEGER(display_width=11)),
    Column('opponent2_id', INTEGER(display_width=11)),
)

user = Table('user', pre_meta,
    Column('id', INTEGER(display_width=11), primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=50)),
    Column('email', VARCHAR(length=100)),
    Column('password', VARCHAR(length=100)),
    Column('scopas', INTEGER(display_width=11)),
    Column('score', INTEGER(display_width=11)),
    Column('games', INTEGER(display_width=11)),
    Column('wins', INTEGER(display_width=11)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['opponents'].drop()
    pre_meta.tables['user'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['opponents'].create()
    pre_meta.tables['user'].create()
