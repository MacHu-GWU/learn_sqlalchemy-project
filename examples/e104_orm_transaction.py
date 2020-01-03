# -*- coding: utf-8 -*-

from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

engine = sa.create_engine("sqlite:///:memory:")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


Base.metadata.create_all(engine)
Session = sessionmaker(engine)


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def run_my_program():
    try:
        with session_scope() as session:
            session.add(User(id=1)) # success but not commit
            session.add_all([User(id=1), User(id=2)]) # failed auto roll back
    except Exception as e:
        print(e)

    session = Session()
    assert session.query(User).count() == 0


if __name__ == "__main__":
    run_my_program()
