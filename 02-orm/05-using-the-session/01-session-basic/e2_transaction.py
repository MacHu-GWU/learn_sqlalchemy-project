# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_psql as engine  # use PostgresSQL engine

Base = orm.declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add_all([
        User(id=1, name="Alice1"),
        User(id=2, name="Bob1"),
        User(id=3, name="Cathy1"),
        User(id=4, name="David1"),
    ])
    ses.commit()

# try with a transaction
with orm.Session(engine) as ses:
    try:
        with ses.begin():
            # update will pass
            ses.execute(sa.update(User).where(User.id == 1).values(name="Alice2"))
            # insert will fail
            ses.add(User(id=2, name="Bob2"))
            ses.commit()
    except:
        pass

# both not changed
with orm.Session(engine) as ses:
    user1 = ses.get(User, 1)
    user2 = ses.get(User, 2)
    assert user1.name == "Alice1"
    assert user2.name == "Bob1"

# this works too
with orm.Session(engine) as ses:
    try:
        ses.execute(sa.update(User).where(User.id == 3).values(name="Cathy2"))
        ses.add(User(id=4, name="David2"))
        ses.commit()
    except:
        ses.rollback()
        pass

with orm.Session(engine) as ses:
    user3 = ses.get(User, 3)
    user4 = ses.get(User, 4)
    print(user3, user4)
