# -*- coding: utf-8 -*-

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

connection = engine.connect()
assert connection.execute(sa.select([t_user]).count()).fetchone()[0] == 0

# transaction
try:
    with connection.begin() as trans:
        connection.execute(t_user.insert(), {"id": 1, "name": "Alice"})
        connection.execute(t_user.insert(), [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
except Exception as e:
    print(e)

assert connection.execute(sa.select([t_user]).count()).fetchone()[0] == 0
connection.close()

