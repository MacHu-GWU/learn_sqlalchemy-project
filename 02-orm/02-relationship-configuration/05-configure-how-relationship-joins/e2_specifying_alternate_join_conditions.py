# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, Session
import sqlalchemy_mate as sam

Base = declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    boston_addresses = relationship(
        "Address",
        primaryjoin="and_(User.id==Address.user_id, Address.city=='Boston')"
    )


class Address(Base, sam.ExtendedBase):
    __tablename__ = "address"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))

    street = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zip = sa.Column(sa.String)


engine = sa.create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as ses:
    ses.add(User(id=1, name="Alice"))
    ses.add(Address(id=1, user_id=1, street="101 st", city="Boston", state="MA", zip="02101"))

    user = ses.get(User, 1)
    print(user)
    print(user.boston_addresses)
