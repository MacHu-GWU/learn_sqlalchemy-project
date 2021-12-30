# -*- coding: utf-8 -*-

import attr
import sqlalchemy as sa
from sqlalchemy.orm import registry, Session
from learn_sqlalchemy.db import engine_sqlite as engine

# equivalent to Base = declarative_base()
mapper_registry = registry()
Base = mapper_registry.generate_base()


@mapper_registry.mapped
@attr.s
class User:
    __table__ = sa.Table(
        "user", mapper_registry.metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
    )

    id: int = attr.ib()
    name: str = attr.ib()


Base.metadata.create_all(engine)

with Session(engine) as ses:
    user = User(id=1, name="Alice")
    print(user)
    print(attr.asdict(user))

    ses.add(user)
    ses.add(User(id=2, name="Bob"))
    ses.commit()

    print(ses.scalars(sa.select(User).where(User.id >= 1)).all())
