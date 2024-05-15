# -*- coding: utf-8 -*-

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.ext.automap import automap_base
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine


def initialize_database(engine):
    Base = declarative_base()

    class User(Base, sam.ExtendedBase):
        __tablename__ = "user"

        id = sa.Column(sa.Integer, primary_key=True)

        posts = relationship("Post", back_populates="author")

    class Post(Base, sam.ExtendedBase):
        __tablename__ = "post"

        id = sa.Column(sa.Integer, primary_key=True)
        title = sa.Column(sa.String)
        author_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))

        author = relationship("User", foreign_keys=[author_id, ])

    Base.metadata.create_all(engine)

    with Session(engine) as ses:
        ses.add(Post(id=1, title="Hello World", author=User(id=1)))
        ses.commit()

        post = ses.get(Post, 1)
        assert post.author_id == 1
        assert post.author.id == 1

        user = ses.get(User, 1)
        assert user.id == 1


initialize_database(engine)

Base = automap_base()

Base.prepare(engine, reflect=True)

User = Base.classes.user
Post = Base.classes.post

with Session(engine) as ses:
    post = ses.get(Post, 1)
    assert post.author_id == 1
    with pytest.raises(AttributeError):
        _ = post.author.id

    user = ses.get(User, 1)
    assert user.id == 1
