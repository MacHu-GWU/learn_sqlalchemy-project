# -*- coding: utf-8 -*-

"""
单类, 单属性的 validator.

Ref:

- https://docs.sqlalchemy.org/en/14/orm/mapped_attributes.html#simple-validators
"""

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()

class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    email = sa.Column(sa.String, primary_key=True)
    password = sa.Column(sa.String)

    @orm.validates("email")
    def validate_email(self, key, value):
        if "@" not in value:
            raise ValueError("failed simple email validation")
        return value

t_user = User.__table__

engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    # 在创建实例的时候, validator 会被调用
    with pytest.raises(ValueError):
        user = User(email="not-valid-user", password="123456")

    with engine.connect() as conn:
        conn.execute(t_user.insert(), {"email": "not-valid-email", "password": "123456"})

    # 在从数据库读取实例的时候, validator 不会被调用
    user = ses.get(User, "not-valid-email")
    print(user)
