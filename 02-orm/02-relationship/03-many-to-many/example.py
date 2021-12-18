# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html?highlight=many%20many#many-to-many
"""

import pytest
import sqlalchemy as sa
import sqlalchemy_mate as sam
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

# --------- Define Schema ---------

# define association table
# third argument is foreign key,
question_and_tag_association_table = sa.Table(
    "question_and_tag", Base.metadata,
    sa.Column("question_id", sa.ForeignKey("questions.id"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tags.id"), primary_key=True),
)


class Question(Base, sam.ExtendedBase):
    """
    A StackOverFlow question.

    每一个 Question 可能有多个Tag。
    """
    __tablename__ = "questions"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, unique=True, index=True)

    tags = relationship(
        "Tag",  # name of other entity
        secondary=question_and_tag_association_table,  # association table
        back_populates="questions",  # will be populated as this in Tag class
    )

    @property
    def n_tag(self):
        return len(self.tags)


class Tag(Base, sam.ExtendedBase):
    """
    A question tag.

    每一个Tag会被关联到很多个Question上。
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


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
