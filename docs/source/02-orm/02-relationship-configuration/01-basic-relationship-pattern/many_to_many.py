# -*- coding: utf-8 -*-

"""
In this example, one question has multiple tags, and a tag is associated with
multiple question. It is a standard many-to-many relationship.

Reference: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many

**中文文档**

每次请只运行一个 example(

注意:

- 如果 entity 实例是通过 session.query 获得的, 那么则会自动跟 session 所绑定. 当你
访问 entity 还没有读到内存中的属性时, 则 sqlalchemy 可以帮你自动从数据库中读取. (只要
你指定了 primary key)
- 如果你是手动创建的 entity 实例, 而不是用 session.query 获得实例, 是不会自动跟 session
所绑定的.
"""

from __future__ import print_function
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import select, text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

# --- Initiate connection ---
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# --- Define Schema ---
# define association table
# third argument is foreign key
question_and_tag = Table(
    "question_and_tag", Base.metadata,
    Column("question_id", Integer, ForeignKey("question.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class Question(Base):
    """
    A StackOverFlow question.
    
    每一个Question可能有多个Tag。
    """
    __tablename__ = "question"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)

    tags = relationship(
        "Tag",  # name of other entity
        secondary=question_and_tag,  # association table
        back_populates="questions",  # will be populated as this in Tag class
    )

    def __repr__(self):
        return "question(id=%r, n_tag=%r)" % (self.id, len(self.tags))

    @classmethod
    def by_id(cls, id, session):
        """
        :rtype: Question
        """
        return session.query(cls).filter(cls.id == id).one()

    @property
    def n_tag(self):
        return len(self.tags)


class Tag(Base):
    """
    A question tag.
    
    每一个Tag会被关联到很多个Question上。
    """
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    questions = relationship(
        "Question",
        secondary=question_and_tag,
        back_populates="tags",
    )

    def __repr__(self):
        return "tag(id=%r, name=%r, n_questions=%r)" % (
            self.id, self.name, len(self.questions))

    @classmethod
    def by_id(cls, id, session):
        """
        :rtype: Tag
        """
        return session.query(cls).filter(cls.id == id).one()

    @property
    def n_question(self):
        return len(self.questions)


Base.metadata.create_all(engine)


def reset():
    engine.execute(question_and_tag.delete())
    engine.execute(Question.__table__.delete())
    engine.execute(Tag.__table__.delete())


reset()


def example_insert_data():
    """
    在没有 primary_key conflict 的情况下插入数据. 一条和多条的情况类似.

    注意, 如果 ``relationship`` 的虚拟 column 已给定, many-to-many 的 association
    数据会自动更新.
    """
    reset()

    tag1 = Tag(id=1, name="Python")
    tag2 = Tag(id=2, name="Python2")
    tag3 = Tag(id=3, name="Python3")
    question_list = [
        Question(id=1, title="question1", tags=[tag1, tag2]),
        Question(id=2, title="question2", tags=[tag2, tag3]),
        Question(id=3, title="question3", tags=[tag3, tag1]),
        Question(id=4, title="question4", tags=[tag1, tag2, tag3]),
    ]
    session.add_all(question_list)
    session.commit()


def print_raw_data():
    for question in session.query(Question):
        print(question)

    for tag in session.query(Tag):
        print(tag)

    for row in engine.execute(select([question_and_tag])):
        print(row)


def example_print_raw_data():
    """
    打印数据库中的数据。
    """
    example_insert_data()
    print_raw_data()


def example_query():
    example_insert_data()

    # find all tags in a question
    question = session.query(Question).filter(Question.id == 1).one()
    assert len(question.tags) == 2

    # find all associated question for a tag
    tag = session.query(Tag).filter(Tag.id == 1).one()
    assert len(tag.questions) == 3

    # find all associated quertion having a tag
    query = session.query(Question.id, Question.title) \
        .join(question_and_tag) \
        .filter(question_and_tag.c.tag_id.in_((1, 2))) \
        .distinct() \
        .order_by(Question.id)
    for res in query:
        print(res)

    # equivalent sql
    stmt = text("""
    SELECT
        DISTINCT id, title
    FROM 
        question 
    JOIN question_and_tag
    ON question.id = question_and_tag.question_id
    WHERE
        question_and_tag.tag_id in (1, 2)
    """)
    # for row in engine.execute(stmt):
    #     print(row)


def example_cascade_update_one():
    """
    ``Session.merge`` 是一个非常强大的方法, 不仅更新 Entity 本身, 所有的 Relationship
    相关的数据也会被自动更新.

    Reference: https://docs.sqlalchemy.org/en/13/orm/session_state_management.html#merging

    注意, 下面这种方法是 **不行的**, 因为它修改了其他的 entity, Tag::

        question = session.query(Question).filter(Question.id==1).one()
        # remove tag1, add tag3, update tag name
        question.tags = [Tag(id=2, name="tag2"), Tag(id=3, name="tag3")]

    但是下面的这种方法 **可行**, 因为它并没有修改其他的 entity, Tag::

        question = Question.by_id(1, session)
        # remove tag1, add tag3
        question.tags = [Tag.by_id(2, session), Tag.by_id(3, session)]
    """
    example_insert_data()

    # before state
    assert Tag.by_id(1, session).n_question == 3
    assert Tag.by_id(3, session).n_question == 3
    assert Tag.by_id(2, session).name == "Python2"
    assert Tag.by_id(3, session).name == "Python3"

    question = Question(
        id=1, title="question1 new",
        tags=[Tag(id=2, name="tag2"), Tag(id=3, name="tag3")],  # remove tag1, add tag3, update tag name
    )
    session.merge(question)
    session.commit()

    # after state
    assert Tag.by_id(1, session).n_question == 2
    assert Tag.by_id(3, session).n_question == 4
    assert Tag.by_id(2, session).name == "tag2"
    assert Tag.by_id(3, session).name == "tag3"


def example_cascade_update_many():
    example_insert_data()

    question_list = [
        Question(id=4, tags=[]),
        Question(
            id=5, tags=[
                Tag.by_id(1, session),
                Tag.by_id(2, session),
                Tag.by_id(3, session),
                Tag(id=4, name="Python4"),
            ]
        )
    ]
    for question in question_list:
        session.merge(question)
        session.commit()

    # after state
    assert Question.by_id(4, session).n_tag == 0
    assert Question.by_id(5, session).n_tag == 4
    assert Tag.by_id(1, session).n_question == 3
    assert Tag.by_id(2, session).n_question == 3
    assert Tag.by_id(3, session).n_question == 3
    assert Tag.by_id(4, session).n_question == 1

    # after state


def example_delete_question():
    """
    删除了 question1, 之后, tag1, tag2 在 association table 中 (第二列), 也应该
    不再与 question1 关联.
    """
    example_insert_data()

    # check before state
    assert Tag.by_id(1, session).n_question == 3
    assert Tag.by_id(2, session).n_question == 3

    question = session.query(Question).filter(Question.id == 1).one()
    session.delete(question)

    # check after state
    assert Tag.by_id(1, session).n_question == 2
    assert Tag.by_id(2, session).n_question == 2


if __name__ == "__main__":
    # example_print_raw_data()
    # example_query()
    # example_cascade_update_one()
    example_cascade_update_many()
    # example_delete_question()

    session.close()
