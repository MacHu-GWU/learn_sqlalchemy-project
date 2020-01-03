# -*- coding: utf-8 -*-

import sqlalchemy as sa

engine = sa.create_engine("sqlite:///:memory:")

metadata = sa.MetaData()
t_user = sa.Table(
    "users_core", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String),
)
metadata.create_all(engine)

print(metadata.tables)
