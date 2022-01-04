# -*- coding: utf-8 -*-

"""
问题:

观察如下电商数据库. 有 Customer 和 Address 两个对象. Customer 有不止一个 address.
如果只有一个 address, 那么简化版本的 ``billing_address = relationship("Address")``
就够了. 但是有多个 address, 你需要显式定义 ``foreign_keys``.
``billing_address = relationship("Address", foreign_keys=[billing_address_id])``

Reference:

- https://docs.sqlalchemy.org/en/latest/orm/join_conditions.html
"""

import sqlalchemy as sa
import sqlalchemy_mate as sam
from sqlalchemy.orm import declarative_base, relationship, Session
from learn_sqlalchemy.db import engine_sqlite as engine

Base = declarative_base()


class Customer(Base, sam.ExtendedBase):
    __tablename__ = "customer"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    billing_address_id = sa.Column(sa.Integer, sa.ForeignKey("address.id"))
    shipping_address_id = sa.Column(sa.Integer, sa.ForeignKey("address.id"))

    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])


class Address(Base, sam.ExtendedBase):
    __tablename__ = "address"

    id = sa.Column(sa.Integer, primary_key=True)
    street = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    zip = sa.Column(sa.String)


Base.metadata.create_all(engine)

with Session(engine) as ses:
    ses.add(Address(id=1, street="101 st", city="Newyork", state="NY", zip="10001"))
    ses.add(Address(id=2, street="102 st", city="Newyork", state="NY", zip="10002"))
    ses.add(Customer(id=1, name="Alice", billing_address_id=1, shipping_address_id=2))
    ses.commit()

    customer: Customer = ses.get(Customer, 1)
    print(customer.billing_address)
    print(customer.shipping_address)
