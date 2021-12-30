# -*- coding: utf-8 -*-

"""
**结论**

1. 不推荐在一个类里同时使用 declarative base 和 attr.
2. attrs_mate 可以一起使用, 不过 nested schema 就不行了. 如果 nested schema
    是一个 DB entity 对象, 那显然应该用 relationship.
"""

import attr
from attrs_mate import AttrsClass
import sqlalchemy as sa
import sqlalchemy_mate as sam
from sqlalchemy.orm import registry, Session
from learn_sqlalchemy.db import engine_sqlite as engine

# equivalent to Base = declarative_base()
mapper_registry = registry()
Base = mapper_registry.generate_base()


@mapper_registry.mapped
@attr.s
class User(AttrsClass):
    __table__ = sa.Table(
        "user", mapper_registry.metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("profile", sa.JSON),
    )

    id: int = attr.ib()
    name: str = attr.ib()


Base.metadata.create_all(engine)

with Session(engine) as ses:
    user = User(id=1, name="Alice")
    ses.add(user)
    ses.commit()

    user = ses.get(User, 1)
    print(user.to_dict())
