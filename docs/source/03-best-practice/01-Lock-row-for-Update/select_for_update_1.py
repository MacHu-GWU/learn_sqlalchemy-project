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


# 清理所有表中的数据, 确保以一个干净的表作为开始
with engine.connect() as conn:
    conn.execute(Job.__table__.delete())
    conn.commit()

# 插入一条数据用于实验
with orm.Session(engine) as ses:
    job = Job(id="job-1", value=0)
    ses.add(job)
    ses.commit()

# 用 with_for_update 获取一条锁, 并且在 30 秒内不会释放
with orm.Session(engine) as ses:
    with ses.begin():
        # 加了 nowait 则当锁被占用时会立刻抛出异常
        stmt = sa.select(Job).where(Job.id == "job-1").with_for_update(nowait=True)
        # 如果不加 nowait, 则不会立刻抛出异常, 而是一直等到获得锁
        # stmt = sa.select(Job).where(Job.id == "job-1").with_for_update()
        job = ses.execute(stmt).scalar_one()
        print(f"Got job {job.id = }, doing a long transaction ...")
        time.sleep(30)
        ses.commit()
        print("Transaction finished")
