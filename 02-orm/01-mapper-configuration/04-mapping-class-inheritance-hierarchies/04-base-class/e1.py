# -*- coding: utf-8 -*-

"""
如何定义一个基类, 这个基类背后并不会有一个 Database Table.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = orm.declarative_base()


class Person(Base, sam.ExtendedBase):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class Engineer(Person):
    __tablename__ = "engineer"

    engineer_level = sa.Column(sa.Integer, nullable=False)


class Manager(Person):
    __tablename__ = "manager"

    manager_level = sa.Column(sa.Integer, nullable=False)


Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    engineer = Engineer(id=1, name="Alice", engineer_level=3)
    ses.add(engineer)

    manager = Manager(id=2, name="Bob", manager_level=1)
    ses.add(manager)

    ses.commit()

with orm.Session(engine) as ses:
    print(sam.pt.from_model(Engineer, ses))
    print(sam.pt.from_model(Manager, ses))
#