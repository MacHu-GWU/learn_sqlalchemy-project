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
    print(users)
# # orm query api returns dict instead of object
# for user in session.execute(session.query(User).statement):
#     dict(user)
#
# # **THERE's NO EASY/PERFORMANCE WAY TO CONVERT ORM object to dict**
#
# # --- update
#
# # atomic update method 1
# # WARNING! don't construct user like this: ``user = User(id=1, name="Alice")``
# # it is created out of session's scope, which is not atomic!
# user = session.query(User).get(1)
# user.name = "Alice"
# session.commit()
#
# assert session.query(User).get(1).name == "Alice"
#
# # atomic update method 2
# session.query(User).filter(User.id == 1).update({User.name: "Ana"})
# session.commit()
# assert session.query(User).get(1).name == "Ana"
#
# # update many
# session.query(User).update({User.name: "Ana"})
# session.commit()
# for user in session.query(User):
#     assert user.name == "Ana"
#
# # --- delete
#
# # delete one
# session.query(User).filter(User.id == 1).delete()
# session.commit()
#
# # delete many
# assert session.query(User).count() == 2
# assert session.query(User).delete()
# assert session.query(User).count() == 0
