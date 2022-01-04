# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = orm.declarative_base()


class ExtendedBase(Base, sam.ExtendedBase):
    __abstract__ = True


class QuestionAndItsTag(ExtendedBase):
    __tablename__ = "asso_question_and_tag"

    question_id = sa.Column("question_id", sa.ForeignKey("questions.question_id"), primary_key=True)
    tag_id = sa.Column("tag_id", sa.ForeignKey("tags.tag_id"), primary_key=True)


class Question(ExtendedBase):
    """
    A StackOverFlow question.

    One question could have multiple tags.
    """
    __tablename__ = "questions"

    question_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, unique=True, index=True)

    tags = orm.relationship(
        "Tag",  # name of other entity
        secondary=QuestionAndItsTag.__table__,  # association table
        back_populates="questions",  # will be populated as this in Tag class
    )


class Tag(ExtendedBase):
    """
    A question tag.

    There could be many questions having this tags.
    """
    __tablename__ = "tags"

    tag_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, index=True)

    questions = orm.relationship(
        "Question",
        secondary=QuestionAndItsTag.__table__,
        back_populates="tags",
    )


Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    q_list = [
        Question(
            question_id=1,
            title="q1",
            tags=[
                Tag(tag_id=1, name="t1"),
                Tag(tag_id=2, name="t2"),
            ],
        ),
        Question(
            question_id=2,
            title="q2",
            tags=[
                Tag(tag_id=2, name="t2"),
                Tag(tag_id=3, name="t3"),
            ],
        ),
        Question(
            question_id=3,
            title="q3",
            tags=[
                Tag(tag_id=3, name="t3"),
                Tag(tag_id=1, name="t1"),
            ],
        ),
    ]
    for q in q_list:
        ses.merge(q)
    ses.commit()

with orm.Session(engine) as ses:
    print(sam.pt.from_model(Question, ses))
    print(sam.pt.from_model(Tag, ses))
    print(sam.pt.from_model(QuestionAndItsTag, ses))
