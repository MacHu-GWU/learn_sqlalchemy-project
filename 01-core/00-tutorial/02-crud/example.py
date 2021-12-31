# -*- coding: utf-8 -*-

"""
- Create / Insert
- Read / Select
- Update
- Delete
"""

import sqlalchemy as sa
from sqlalchemy import exc

engine = sa.create_engine("sqlite:///:memory:")

metadata = sa.MetaData()
t_user = sa.Table(
    "users", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String),
)
metadata.create_all(engine)

#--- create

# insert one
engine.execute(t_user.insert(), {"id": 1, "name": "Alice"})

# insert many
engine.execute(t_user.insert(), [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Cathy"}])

# handle primary key conflict method 1
connection = engine.connect()
trans = connection.begin()

try:
    connection.execute(t_user.insert(), {"id": 3, "name": "Cathy"})
    trans.commit()
except exc.IntegrityError:
    trans.rollback()

# handle primary key conflict method 2
try:
    engine.execute(t_user.insert(), {"id": 3, "name": "Cathy"})
except exc.IntegrityError:
    pass

#---read

# fetch one record
print(engine.execute(sa.select([t_user]).where(t_user.c.id==1)).fetchone())# (1, 'Alice')

# fetch many records
print(engine.execute(sa.select([t_user])).fetchall()) # [(1, 'Alice'), (2, 'Bob'), (3, 'Cathy')]

# fetch only part of records
cursor = engine.execute(sa.select([t_user]))
print(cursor.fetchmany(2)) # [(1, 'Alice'), (2, 'Bob')]
print(cursor.fetchmany(2)) # [(3, 'Cathy')]

# convert sqlalchemy.engine.result.RowProxy' to tuple, list, dict
for row in engine.execute(sa.select([t_user])):
    print(type(row), tuple(row), list(row), dict(row))

#--- update

# update one
engine.execute(t_user.update().where(t_user.c.id==1).values(name="Ana"))
assert engine.execute(sa.select([t_user]).where(t_user.c.id==1)).fetchone()["name"] == "Ana"

# update many
engine.execute(t_user.update().values(name="Ana"))
assert engine.execute(sa.select([t_user]).where(t_user.c.id==3)).fetchone()["name"] == "Ana"

#--- delete

# delete one
engine.execute(t_user.delete().where(t_user.c.id==1))
assert engine.execute(sa.select([t_user]).count()).fetchone()[0] == 2

# delete many
engine.execute(t_user.delete())
assert engine.execute(sa.select([t_user]).count()).fetchone()[0] == 0
