# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import registry

# equivalent to Base = declarative_base()
mapper_registry = registry()
Base = mapper_registry.generate_base()


# an example mapping using the base
class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    fullname = sa.Column(sa.String)
    nickname = sa.Column(sa.String)
