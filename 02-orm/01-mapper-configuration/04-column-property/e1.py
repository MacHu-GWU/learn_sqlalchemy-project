# -*- coding: utf-8 -*-

"""
Co

Ref:

- https://docs.sqlalchemy.org/en/latest/orm/mapped_sql_expr.html#mapper-column-property-sql-expressions
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()

def example1():
    class User(Base):
        __tablename__ = "user"

        id = sa.Column(sa.Integer, primary_key=True)
        firstname = sa.Column(sa.String)
        lastname = sa.Column(sa.String)

        fullname = orm.column_property(firstname + " " + lastname)

    engine = sam.EngineCreator().create_sqlite()
    Base.metadata.create_all(engine)

    with orm.Session(engine) as ses:
        user = User(id=1, firstname="Alice", lastname="Wu")
        print(user.fullname)
        ses.add(user)
        ses.commit()

        user = ses.get(User, 1)
        print(user.fullname)

        with engine.connect() as conn:
            row = conn.execute(sa.select(User.__table__)).one()
            print(row)
