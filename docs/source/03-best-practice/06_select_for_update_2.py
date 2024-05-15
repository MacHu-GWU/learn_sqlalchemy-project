# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id: orm.Mapped[str] = orm.mapped_column(sa.String, primary_key=True)
    value: orm.Mapped[int] = orm.mapped_column(sa.Integer)


engine = sam.EngineCreator(
    username="postgres",
    password="password",
    database="postgres",
    host="localhost",
    port=40311,
).create_postgresql_pg8000()
Base.metadata.create_all(engine)


with orm.Session(engine) as ses:
    job = ses.get(Job, "job-1")
    print(f"{job.id = }, {job.value = }")  # this will print

    job.value = 1
    ses.commit()  # this will not work until the lock is released

with orm.Session(engine) as ses:
    job = ses.get(Job, "job-1")
    print(f"{job.id = }, {job.value = }")
