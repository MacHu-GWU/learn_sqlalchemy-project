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

# 在一个 transaction 中尝试获取锁, 当然由于另一个程序已经在运行了, 所以肯定会失败.
with orm.Session(engine) as ses:
    with ses.begin():
        stmt = sa.select(Job).where(Job.id == "job-1").with_for_update(nowait=True)
        job = ses.execute(stmt).scalar_one()
        print(f"before: {job.id = }, {job.value = }")  # this will print
        job.value = 1
        ses.commit()  # this will not work

    job = ses.get(Job, "job-1")
    print(f"after: {job.id = }, {job.value = }")
