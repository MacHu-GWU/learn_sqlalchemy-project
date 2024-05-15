# -*- coding: utf-8 -*-

import time
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

with engine.connect() as conn:
    conn.execute(Job.__table__.delete())
    conn.commit()

with orm.Session(engine) as ses:
    job = Job(id="job-1", value=0)
    ses.add(job)
    ses.commit()

with orm.Session(engine) as ses:
    with ses.begin():
        stmt = sa.select(Job).where(Job.id == "job-1").with_for_update(nowait=True)
        job = ses.execute(stmt).scalar_one()
        print(f"Got job {job.id = }, doing a long transaction ...")
        time.sleep(30)
        ses.commit()
