# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

engine = sa.create_engine("sqlite:///:memory:")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


Base.metadata.create_all(engine)
