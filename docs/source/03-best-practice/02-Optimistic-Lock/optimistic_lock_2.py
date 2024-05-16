# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id: orm.Mapped[str] = orm.mapped_column(sa.String, primary_key=True)
    version_id: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    value: orm.Mapped[int] = orm.mapped_column(sa.Integer)


engine = sam.EngineCreator(
    username="postgres",
    password="password",
    database="postgres",
    host="localhost",
    port=40311,
).create_postgresql_pg8000()
Base.metadata.create_all(engine)


# 清理所有表中的数据, 确保以一个干净的表作为开始
with engine.connect() as conn:
    conn.execute(Job.__table__.delete())
    conn.commit()

# 插入一条数据用于实验
with orm.Session(engine) as ses:
    job = Job(id="job-1", version_id=0, value=0)
    ses.add(job)
    ses.commit()


with orm.Session(engine) as ses:
    with ses.begin():
        stmt = sa.select(Job).where(Job.id == "job-1")
        job = ses.execute(stmt).scalar_one()
        new_version_id = job.version_id + 1
        stmt = (
            sa.update(Job)
            .where(sa.and_(Job.id == job.id, Job.version_id == job.version_id))
            .values(version_id=new_version_id, value=2)
        )
        res = ses.execute(stmt)
        ses.commit()
        if res.rowcount == 1:
            print("optimistic lock update succeeded")
        else:
            print("optimistic lock update failed")

with orm.Session(engine) as ses:
    job = ses.get(Job, "job-1")
    print(f"{job.id = }, {job.version_id = }, {job.value = }")
