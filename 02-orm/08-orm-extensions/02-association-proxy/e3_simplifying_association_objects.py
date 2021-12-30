# -*- coding: utf-8 -*-

"""
应用场景:

有一个博客的 App, 一个博客就是一个 Post, 每个 Post 可能有多个 Tag. 所以 Post / Tag 是
Many to Many 的关系.

结论:

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, relationship
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


class Post(Base, sam.ExtendedBase):
    __tablename__ = "post"

    post_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(length=128))

    # proxy the "name" attribute from the "tags" relationship
    # tags_proxy = association_proxy(target_collection="tags", attr="name")


class Tag(Base, sam.ExtendedBase):
    __tablename__ = "tag"

    tag_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=64))


class PostAndTag(Base, sam.ExtendedBase):
    __tablename__ = "post_and_tag"

    post_id = sa.Column(sa.Integer, sa.ForeignKey("post.post_id"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("tag.tag_id"), primary_key=True)
    update_time = sa.Column(sa.DateTime)


Base.metadata.create_all(engine)

with Session(engine) as ses:
    post = Post(post_id=1, title="Hello World")
    post.tags_proxy.append("Python")
    post.tags_proxy.append("Sqlalchemy")
    print(post.tags)

    ses.add(post)
    ses.commit()

    print(sam.pt.from_everything(Tag, engine))
    print(sam.pt.from_everything(Post, engine))
    print(sam.pt.from_everything(t_post_and_tag, engine))
