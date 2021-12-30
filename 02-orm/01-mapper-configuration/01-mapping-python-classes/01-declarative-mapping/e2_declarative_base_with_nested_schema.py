# -*- coding: utf-8 -*-

import attr
from attrs_mate import AttrsClass
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

# --- Implement a json serializable attrs class
import json
from sqlalchemy.dialects.postgresql.base import ischema_names

try:
    from sqlalchemy.dialects.postgresql import JSON

    has_postgres_json = True
except ImportError:
    class PostgresJSONType(sa.types.UserDefinedType):
        """
        Text search vector type for postgresql.
        """

        def get_col_spec(self):
            return 'json'


    ischema_names['json'] = PostgresJSONType
    has_postgres_json = False


class AttrsJsonType(sa.types.TypeDecorator):
    """
    JSONType offers way of saving JSON data structures to database. On
    PostgreSQL the underlying implementation of this data type is 'json' while
    on other databases its simply 'text'.

    ::

        from sqlalchemy_utils import JSONType


        class Product(Base):
            __tablename__ = 'product'
            id = sa.Column(sa.Integer, autoincrement=True)
            name = sa.Column(sa.Unicode(50))
            details = sa.Column(JSONType)


        product = Product()
        product.details = {
            'color': 'red',
            'type': 'car',
            'max-speed': '400 mph'
        }
        session.commit()
    """
    impl = sa.UnicodeText
    cache_ok = True

    def __init__(self, *args, **kwargs):
        if "attrs_class" in kwargs:
            self.attrs_class = kwargs.pop("attrs_class")
        else:
            raise ValueError

        super(AttrsJsonType, self).__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use the native JSON type.
            if has_postgres_json:
                return dialect.type_descriptor(JSON())
            else:
                return dialect.type_descriptor(PostgresJSONType())
        else:
            return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql' and has_postgres_json:
            return value
        if value is not None:
            value = value.to_json()
        return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        if value is not None:
            value = self.attrs_class.from_json(value)
        return value


# declarative base class
Base = declarative_base()


@attr.s
class AttrsJsonColumn(AttrsClass):
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, value):
        return cls.from_dict(json.loads(value))


@attr.s
class Profile(AttrsJsonColumn):
    dob: str = attr.ib()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    profile = sa.Column(AttrsJsonType(attrs_class=Profile))


Base.metadata.create_all(engine)

with Session(engine) as ses:
    ses.add(User(id=1, name="Alice", profile=Profile(dob="2021-01-01")))
    ses.commit()

    user = ses.get(User, 1)
    print(user.profile)

    user_data = user.to_dict()
    print(user.to_dict())

    user = User(**user_data)
    print(user)
