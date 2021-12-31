# -*- coding: utf-8 -*-

"""
Composite Column Types
"""

import attr
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


@attr.s
class Point:
    x: int = attr.ib()
    y: int = attr.ib()

    def __composite_values__(self):
        return (self.x, self.y)


class Vertex(Base, sam.ExtendedBase):
    __tablename__ = "vertex"

    id = sa.Column(sa.Integer, primary_key=True)
    x1 = sa.Column(sa.Integer)
    y1 = sa.Column(sa.Integer)
    x2 = sa.Column(sa.Integer)
    y2 = sa.Column(sa.Integer)

    start = orm.composite(Point, x1, y1)
    end = orm.composite(Point, x2, y2)


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    v = Vertex(id=1, start=Point(x=0, y=0), end=Point(x=1, y=1))
    ses.add(v)
    ses.commit()

    stmt = sa.select(Vertex).where(Vertex.start == Point(0, 0))
    v = ses.scalars(stmt).one()
    print(v)
    print(v.start)
