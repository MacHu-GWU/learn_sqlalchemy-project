# -*- coding: utf-8 -*-

"""
本例中我们提供了一个较为复杂的实际用例 - 程序员问答网站 StackOverFlow

数据库中有这么几个对象:

- User: 网站用户, 用户可以发问题 Question
- Question: 用户发的贴子, 每一个贴子有且只有一个提问者 User, 每个贴子还可能有多个 Tag
- Test:


Reference:

- https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html?highlight=many%20many#many-to-many
"""

import pytest
import sqlalchemy as sa
import sqlalchemy_mate as sam
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

prefix = "comprehend_relationship_demo"

# --------- Define Schema ---------
class User(Base, sam.ExtendedBase):
    """

    """
    __tablename__ = f"{prefix}_users"

    id = sa.Column(Integer, primary_key=True)
    name = Column(String)
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return "Department(id=%r, name=%r)" % (self.id, self.name)


# define association table
# third argument is foreign key,
t_asso_q_and_t = sa.Table(
    "question_and_tag", Base.metadata,
    sa.Column("question_id", sa.ForeignKey("questions.id"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tags.id"), primary_key=True),
)


class Question(Base, sam.ExtendedBase):
    """
    A StackOverFlow question.

    One question could have multiple tags.
    """
    __tablename__ = "questions"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, unique=True, index=True)

    tags = relationship(
        "Tag",  # name of other entity
        secondary=t_asso_q_and_t,  # association table
        back_populates="questions",  # will be populated as this in Tag class
    )

    @property
    def n_tag(self):
        return len(self.tags)


class Tag(Base, sam.ExtendedBase):
    """
    A question tag.

    There could be many questions having this tags.
    """
    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, index=True)

    questions = relationship(
        "Question",
        secondary=question_and_tag_association_table,
        back_populates="tags",
    )

    @property
    def n_question(self):
        return len(self.questions)


engine = sam.EngineCreator(
    host="localhost",
    port=43348,
    database="postgres",
    username="postgres",
    password="password",
).create_postgresql_pg8000()
sam.test_connection(engine, timeout=3)


class Test:
    @classmethod
    def setup_class(cls):
        question_and_tag_association_table
        Question
        Tag

        tag_py = Tag(id=1, name="Python")
        tag_py2 = Tag(id=2, name="Python2")
        tag_py3 = Tag(id=3, name="Python3")
        q_list = [
            Question(id=1, title="question1", tags=[tag_py, tag_py2]),
            Question(id=2, title="question2", tags=[tag_py2, tag_py3]),
            Question(id=3, title="question3", tags=[tag_py3, tag_py]),
            Question(id=4, title="question4", tags=[tag_py, tag_py2, tag_py3]),
        ]
        Question.smart_insert(engine, q_list)
        # with Session(engine) as ses:


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
