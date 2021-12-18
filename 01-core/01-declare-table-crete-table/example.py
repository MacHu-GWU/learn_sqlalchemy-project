# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.sqlalchemy.org/en/14/core/metadata.html
"""

import typing
import sqlalchemy as sa
from rich import print

# define metadata store
metadata = sa.MetaData()

# define a table
t_user = sa.Table(
    "users", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String),
)

engine = sa.create_engine("sqlite:///:memory:")
metadata.create_all(engine)

# dict view of table, key is table name
_: typing.Dict[str, sa.Table] = metadata.tables

# list view of table, element is table
_: typing.List[sa.Table] = metadata.sorted_tables

# access table
assert metadata.tables["users"] is t_user
assert metadata.sorted_tables[0] is t_user

# dict view of columns
for column_name, column in t_user.c.items():
    assert isinstance(column_name, str)
    assert isinstance(column, sa.Column)

for column in t_user.c:
    assert isinstance(column, sa.Column)

# access columns
assert t_user.c.id.name == "id"
assert t_user.c["id"].name == "id"

# get the table's primary key columns
for column in t_user.primary_key:
    assert column.name == "id"

# get the table's foreign key objects:
for column in t_user.foreign_keys:
    pass

# access a column's table:
assert t_user.c.id.table is t_user
