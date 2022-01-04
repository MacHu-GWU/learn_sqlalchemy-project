# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.sqlalchemy.org/en/latest/orm/join_conditions.html?highlight=article#overlapping-foreign-keys
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, Session
import sqlalchemy_mate as sam

Base = declarative_base()


class Author(Base, sam.ExtendedBase):
    __tablename__ = "authors"

    lastname = sa.Column(sa.String, primary_key=True)
    firstname = sa.Column(sa.String, primary_key=True)


class Article(Base, sam.ExtendedBase):
    __tablename__ = "articles"

    article_id = sa.Column(sa.Integer, primary_key=True)


class ArticleAndAuthor(Base, sam.ExtendedBase):
    __tablename__ = "article_and_authors"

    article_id = sa.Column(sa.Integer, primary_key=True)
    author_lastname = sa.Column(sa.String, primary_key=True)
    author_firstname = sa.Column(sa.String, primary_key=True)

    author = relationship(
        "Author",
        primaryjoin="and_(Author.lastname == foreign(ArticleAndAuthor.author_lastname), Author.firstname == ArticleAndAuthor.author_firstname)"
    )


engine = sa.create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as ses:
    ses.add(Author(lastname="last1", firstname="first1"))
    ses.add(Article(article_id=1))
    ses.add(ArticleAndAuthor(article_id=1, author_lastname="last1", author_firstname="first1"))
    ses.commit()

    aaa = ses.get(ArticleAndAuthor, (1, "last1", "first1"))
    print(aaa.author)
