# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.sqlalchemy.org/en/14/orm/join_conditions.html?highlight=article#custom-operators-based-on-sql-functions
- https://docs.sqlalchemy.org/en/14/core/functions.html
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, remote, foreign, Session
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine


Base = declarative_base()

class OneDimensionPoint(Base, sam.ExtendedBase):
    __tablename__ = "one_dimension_point"

    coordinator = sa.Column(sa.Integer, primary_key=True)

    neighbors = relationship(
        "OneDimensionPoint",
        primaryjoin=sa.func.abs(remote(coordinator) - foreign(coordinator)) <= 2,
        # primaryjoin="func.abs(OneDimensionPoint.coordinator - foreign(OneDimensionPoint.coordinator)) <= 2",
        viewonly=True,
    )

Base.metadata.create_all(engine)

with Session(engine) as ses:
    ses.add_all([
        OneDimensionPoint(coordinator=i)
        for i in range(1, 10+1)
    ])
    ses.commit()

    # stmt = sa.select(OneDimensionPoint).where(sa.func.abs(OneDimensionPoint.coordinator - 5) <= 2)
    # sa.func.abs()
    # results = ses.scalars(stmt).all()
    # print(results)

    # p = ses.get(OneDimensionPoint, 5)
    # print(p)

    stmt = sa.text("""
    SELECT p1.coordinator
    FROM one_dimension_point p1
    JOIN one_dimension_point p2
    WHERE (p1.coordinator - p2.coordinator)
    """)
    results = ses.scalars(stmt).all()
    print(results)
