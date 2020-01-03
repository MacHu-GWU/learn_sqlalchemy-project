# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

engine = sa.create_engine("sqlite:///:memory:")


def get_n_tables():
    metadata = sa.MetaData()
    metadata.reflect(engine)
    return len(metadata.tables)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class Post(Base):
    __tablename__ = "posts"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)


Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()

# --- delete all table
assert get_n_tables() == 2
User.__table__.drop(engine)
assert get_n_tables() == 1
Base.metadata.drop_all(engine)
assert get_n_tables() == 0
