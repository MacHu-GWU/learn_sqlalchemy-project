# -*- coding: utf-8 -*-

import sqlalchemy as sa

engine = sa.create_engine("sqlite:///:memory:")


def get_n_tables():
    metadata = sa.MetaData()
    metadata.reflect(engine)
    return len(metadata.tables)


metadata = sa.MetaData()
t_user = sa.Table(
    "users", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String),
)
t_post = sa.Table(
    "posts", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("title", sa.String),
)
metadata.create_all(engine)

# --- delete one table
assert get_n_tables() == 2
t_user.drop(engine)
assert get_n_tables() == 1  # users been dropped

# --- delete all table
metadata.drop_all(engine)
assert get_n_tables() == 0
