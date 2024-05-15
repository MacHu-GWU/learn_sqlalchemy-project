# -*- coding: utf-8 -*-

"""
应用场景:

有一个博客的 App, 一个博客就是一个 Post, 每个 Post 可能有多个 Tag. 所以 Post / Tag 是
Many to Many 的关系.

结论:

该语法给出了对如何建立 association 更明确的定义, 推荐使用.
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, relationship
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

t_post_and_tag = sa.Table(
    "post_and_tag", Base.metadata,
    sa.Column("post_id", sa.Integer, sa.ForeignKey("post.post_id"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tag.tag_id"), primary_key=True)
)


class Tag(Base, sam.ExtendedBase):
    __tablename__ = "tag"

    tag_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=64))

    @classmethod
    def from_name(cls, name):
        tag_id = hash(name)
        return cls(tag_id=tag_id, name=name)


class Post(Base, sam.ExtendedBase):
    __tablename__ = "post"

    post_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(length=128))

    tags = relationship("Tag", secondary=lambda: t_post_and_tag)

    # proxy the "name" attribute from the "tags" relationship
    # creator explicitly factory method for Tag
    tags_proxy = association_proxy(
        target_collection="tags", attr="name",
        creator=Tag.from_name,
    )


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
