# -*- coding: utf-8 -*-

"""
- (C) Create / Insert
- (R) Read / Select
- (U) Update
- (D) Delete
"""

import sqlalchemy as sa
from sqlalchemy import orm, exc, engine as eng
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    value = sa.Column(sa.Integer)


engine = sa.create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

# --- INSERT
with orm.Session(engine) as ses:
    # insert one
    ses.add(User(id=1, name="Alice", value=1))
    ses.commit()

    # insert many
    ses.add_all([User(id=2, name="Bob", value=2), User(id=3, name="Cathy")])
    ses.commit()

    # handle primary key conflict
    try:
        ses.add(User(id=1))
        ses.commit()
    except exc.IntegrityError:
        ses.rollback()

# --- SELECT
with orm.Session(engine) as ses:
    # fetch one row using primary key columns
    user = ses.get(User, 1)
    assert user.id == 1

    # use where
    stmt = sa.select(User).where(User.id == 1)
    user = ses.scalars(stmt).one()
    assert user.id == 1

    # fetch many records, return iterator

    # fetch many record
    users = ses.scalars(sa.select(User)).all()
    assert [u.id for u in users] == [1, 2, 3]

    # ``Result`` iterator
    result: eng.ScalarResult = ses.scalars(sa.select(User))
    for user in result.fetchmany(2):
        pass

    # use WHERE to filter results
    stmt = sa.select(User).where(User.id <= 2)
    users = ses.scalars(stmt).all()
    assert [u.id for u in users] == [1, 2]

    #
    stmt = sa.select(sa.func.distinct(User.name))
    users = ses.scalars(stmt).all()
    assert users == ['Alice', 'Bob', 'Cathy']

# --- UPDATE

# atomic update method 1
# WARNING! don't construct user like this: ``user = User(id=1, name="Alice")``
# it is created out of session's scope, which is not atomic!
with orm.Session(engine) as ses:
    user = ses.get(User, 1)
    user.name = "Alice1"
    ses.commit()

with orm.Session(engine) as ses:
    assert ses.get(User, 1).name == "Alice1"

# atomic update method 2
with orm.Session(engine) as ses:
    stmt = sa.update(User).where(User.id == 1).values(name="Alice2")
    ses.execute(stmt)
    ses.commit()

with orm.Session(engine) as ses:
    assert ses.get(User, 1).name == "Alice2"

# atomic update method 3
# WARNING! don't do this! this is not multi thread safe:
# user = ses.get(User, 1)
# user.value += 1
# ses.commit()
with orm.Session(engine) as ses:
    before_value = ses.get(User, 1).value
    stmt = sa.update(User).where(User.id == 1).values(value=User.value + 1)
    res = ses.execute(stmt)
    assert res.rowcount == 1
    ses.commit()
    after_value = ses.get(User, 1).value
    assert (after_value - before_value) == 1

# --- DELETE
# delete one
with orm.Session(engine) as ses:
    ses.add(User(id=10))
    ses.commit()

    user = ses.get(User, 10)
    res = ses.delete(user)
    ses.commit()

    assert ses.get(User, 10) is None

# delete many
with orm.Session(engine) as ses:
    ses.add_all([User(id=11), User(id=12), User(id=13)])
    ses.commit()

    stmt = sa.delete(User).where(User.id >= 11)
    res = ses.execute(stmt)
    assert res.rowcount == 3
    ses.commit()
