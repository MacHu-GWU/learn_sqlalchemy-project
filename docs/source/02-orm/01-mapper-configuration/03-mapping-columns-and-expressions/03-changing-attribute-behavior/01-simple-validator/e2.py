# -*- coding: utf-8 -*-

"""
多个类, 设计 relationship 时的 validator.

Ref:

- https://docs.sqlalchemy.org/en/14/orm/mapped_attributes.html#simple-validators
"""

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Email(Base, sam.ExtendedBase):
    __tablename__ = "email"

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    user = orm.relationship("User", back_populates="emails")

class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    emails = orm.relationship("Email", back_populates="user")

    @orm.validates("emails")
    def validate_email(self, key, email):
        if '@' not in email.email:
            raise ValueError("failed simplified email validation")
        return email


# t_user = User.__table__

engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add(User(id=1))
    ses.add_all([
        Email(id=1, email="a@gmail.com", user_id=1),
        Email(id=2, email="b@gmail.com", user_id=1),
        Email(id=3, email="c@gmail.com", user_id=1),
    ])
    ses.commit()

    user = ses.get(User, 1)
    user.emails.append(Email(id=4, email="d@example.com"))
    with pytest.raises(ValueError):
        user.emails.append(Email(id=5, email="not-valid-email"))
    ses.commit()

    user = ses.get(User, 1)
    print(user.emails) # id 1, 2, 3, 4

    email = ses.get(Email, 4)
    print(email.user)
