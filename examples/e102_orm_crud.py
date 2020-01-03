# -*- coding: utf-8 -*-

"""
- Create / Insert
- Read / Select
- Update
- Delete
"""

import sqlalchemy as sa
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

engine = sa.create_engine("sqlite:///:memory:")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    def __repr__(self):
        return "User(id=%r, name=%r)" % (self.id, self.name)


Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()

# --- create

# insert one
session.add(User(id=1))
session.commit()

# insert many
session.add_all([User(id=2), User(id=3)])
session.commit()

# handle primary key conflict
try:
    session.add(User(id=1))
    session.commit()
except exc.IntegrityError:
    session.rollback()

# ---read

# fetch one record, session.query(...).one()
user = session.query(User).filter(User.id==1).one()
assert user.id == 1

# fetch many records, session.query(...).all()
users = session.query(User).all()
assert len(users) == 3

# fetch only part of records
query = session.query(User)
for row in query.yield_per(2):
    pass

# orm query api returns dict instead of object
for user in session.execute(session.query(User).statement):
    dict(user)

# **THERE's NO EASY/PERFORMANCE WAY TO CONVERT ORM object to dict**

#--- update

# atomic update method 1
# WARNING! don't construct user like this: ``user = User(id=1, name="Alice")``
# it is created out of session's scope, which is not atomic!
user = session.query(User).get(1)
user.name = "Alice"
session.commit()

assert session.query(User).get(1).name == "Alice"

# atomic update method 2
session.query(User).filter(User.id==1).update({User.name: "Ana"})
session.commit()
assert session.query(User).get(1).name == "Ana"

# update many
session.query(User).update({User.name: "Ana"})
session.commit()
for user in session.query(User):
    assert user.name == "Ana"

#--- delete

# delete one
session.query(User).filter(User.id==1).delete()
session.commit()

# delete many
assert session.query(User).count() == 2
assert session.query(User).delete()
assert session.query(User).count() == 0
