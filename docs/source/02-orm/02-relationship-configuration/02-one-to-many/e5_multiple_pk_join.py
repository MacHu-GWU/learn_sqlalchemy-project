# -*- coding: utf-8 -*-

"""
有的时候用于单个属性的 relationship 的 join 会涉及到多个 primary key. 本例实验了正确的语法.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = orm.declarative_base()


class ExtendedBase(Base, sam.ExtendedBase):
    __abstract__ = True


class A(ExtendedBase):
    __tablename__ = "a"

    pk_a_1 = sa.Column(sa.Integer, primary_key=True)
    pk_a_2 = sa.Column(sa.Integer, primary_key=True)

    b_list = orm.relationship(
        "B",
        primaryjoin="and_(B.pk_a_1 == A.pk_a_1, B.pk_a_2 == A.pk_a_2)",
        back_populates="a",
    )


class B(ExtendedBase):
    __tablename__ = "b"

    pk_b = sa.Column(sa.Integer, primary_key=True)
    pk_a_1 = sa.Column(sa.Integer, sa.ForeignKey("a.pk_a_1"))
    pk_a_2 = sa.Column(sa.Integer, sa.ForeignKey("a.pk_a_2"))

    a = orm.relationship(
        "A",
        foreign_keys=[pk_a_1, pk_a_2],
        primaryjoin="and_(A.pk_a_1 == B.pk_a_1, A.pk_a_2 == B.pk_a_2)",
        back_populates="b_list",
    )


Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add(A(pk_a_1=1, pk_a_2=1))
    ses.commit()

    ses.add(B(pk_b=1, pk_a_1=1, pk_a_2=1))
    ses.add(B(pk_b=2, pk_a_1=1, pk_a_2=1))
    ses.commit()

with orm.Session(engine) as ses:
    a = ses.get(A, (1, 1))
    print(a.b_list)

    b = ses.get(B, 1)
    print(b.a)
