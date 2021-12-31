# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, relationship
import sqlalchemy_mate as sam

Base = declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "users"

    user_id: int = sa.Column(sa.Integer, primary_key=True)

    comments = relationship("Comment", back_populates="author")
    thumbups = relationship("ThumbUp", back_populates="author")


class Comment(Base, sam.ExtendedBase):
    __tablename__ = "comments"

    post_id: int = sa.Column(sa.Integer, primary_key=True)
    nth_comment: int = sa.Column(sa.Integer, primary_key=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"))

    author = relationship("User", foreign_keys=[author_id,])
    thumbups = relationship("ThumbUp", back_populates="comment")


class ThumbUp(Base, sam.ExtendedBase):
    __tablename__ = "thumbups"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), primary_key=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey("comments.post_id"), primary_key=True)
    nth_comment = sa.Column(sa.Integer, sa.ForeignKey("comments.nth_comment"), primary_key=True)

    author = relationship("User", foreign_keys=[user_id,])
    comment = relationship("Comment", foreign_keys=[post_id, nth_comment])


engine = sa.create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)


def print_all(engine):
    print(f"=== Table({User.__tablename__}) ===")
    print(sam.pt.from_everything(User, engine))
    print(f"=== Table({Comment.__tablename__}) ===")
    print(sam.pt.from_everything(Comment, ses))
    print(f"=== Table({ThumbUp.__tablename__}) ===")
    print(sam.pt.from_everything(ThumbUp, ses))


with Session(engine) as ses:
    ses.add(User(user_id=1))
    ses.add(Comment(post_id=1, nth_comment=1, author_id=1))
    ses.add(ThumbUp(user_id=1, post_id=1, nth_comment=1))
    ses.commit()

    user = ses.get(User, 1)
    print(user.comments)

    comment = ses.get(Comment, (1, 1))
    print(comment.author)

    # thumbup = ses.get(ThumbUp, (1, 1, 1))
    # print(thumbup.author.user_id)

# print_all(engine)

# ses.add(ThumbUp(user_id=1))
