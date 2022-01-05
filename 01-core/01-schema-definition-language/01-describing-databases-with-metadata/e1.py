# -*- coding: utf-8 -*-

"""
知识点:

1. 定义 Metadata
2. 定义 Table
3. 访问 Table 的实例
4. 创建 Engine
5. create, drop Table

Reference:

- https://docs.sqlalchemy.org/en/14/core/metadata.html
"""

import sqlalchemy as sa

# Metadata is a container object keeps together many different features of a database (or multiple databases) being described.
# Create a metadata object
metadata = sa.MetaData()

# Declare a database table
t_user = sa.Table(
    "user", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
)

# Accessing Tables and Columns
# access by list style
_: list = metadata.sorted_tables
table: sa.Table
for table in metadata.sorted_tables:
    assert isinstance(table, sa.Table)
    assert isinstance(table.name, str)

# access by dict style
_: dict = metadata.tables
for table_name, table in metadata.tables.items():
    assert isinstance(table_name, str)
    assert isinstance(table, sa.Table)

# Creating and Dropping Database Tables
# you need to define an database engine first
# this will not start real connection to database, declare it only
engine = sa.create_engine("sqlite:///:memory:", echo=False)

# Create all table and foreign key constrain in dependency order
# Now it really talk to the database
metadata.create_all(engine)

# Drop all table in opposite way
metadata.drop_all(engine)

# You can create / drop individual table too
# ``checkfirst`` parameter  will exam the existing state and raise no error
t_user.drop(engine, checkfirst=True)
t_user.create(engine)
t_user.create(engine, checkfirst=True)
