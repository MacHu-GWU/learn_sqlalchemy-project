# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, foreign, remote, Session
from sqlalchemy.dialects.postgresql import INET
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_psql as engine

Base = declarative_base()


class HostEntry(Base, sam.ExtendedBase):
    __tablename__ = "host_entry"

    id = sa.Column(sa.Integer, primary_key=True)
    ip_address = sa.Column(INET)
    content = sa.Column(sa.String(50))

    # relationship() using explicit foreign() and remote() annotations
    # in lieu (代替) of separate arguments
    parent_host = relationship(
        "HostEntry",
        primaryjoin=remote(ip_address) == sa.cast(foreign(content), INET),
    )

Base.metadata.create_all(engine)

with Session(engine) as ses:
    HostEntry.delete_all(ses)
    data = [
        HostEntry(id=1, ip_address="127.0.0.1", content="127.0.0.3"),
        HostEntry(id=2, ip_address="127.0.0.2", content="127.0.0.1"),
    ]
    HostEntry.smart_insert(ses, data)

    he = ses.get(HostEntry, 2)
    print(he.parent_host)