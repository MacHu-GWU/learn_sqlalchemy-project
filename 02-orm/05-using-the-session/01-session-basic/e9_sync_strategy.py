# -*- coding: utf-8 -*-

"""
Sync Strategy 是只有在 UPDATE 和 DELETE 操作中会出现的概念.

简单来说, 当你使用 ORM 对一个 instance 执行 UPDATE / DELETE 之后, 但还没有 Commit
 的这个阶段. 这个内存中的 instance 的数据是如何跟数据库中的数据同步的.

Sqlalchemy 有三种 Sync 的模式. 这三种模式都是在
sqlalchemy.update 或 sqlalchemy.delete 之后链式调用
execution_options(synchronize_session="evaluate") 来指定的.

1. False, 不进行任何同步. 被 Update 后, Commit 之前, Instance 的数据不会发生变化. 该方法最安全, 不做任何假设, 最为推荐在生产环境的代码中使用.
2. "fetch", 从数据库段获得最新的数据, 这将是一个数据库 API 调用的来回, 开销较大. 数据永远保持最新, 最为稳定, 但是开销较大.
3. "evaluate", 根据 where, values 中的值更新数据, 不需要跟数据库互动. 方便于开发, 是前两者的平衡的结果. 也是默认的方式.
"""

import sqlalchemy as sa
from sqlalchemy import orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = orm.declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add_all([
        User(id=1, name="Alice1"),
        User(id=2, name="Bob1"),
        User(id=3, name="Cathy1"),
        User(id=4, name="David1"),
    ])
    ses.commit()

with orm.Session(engine) as ses:
    user = ses.get(User, 1)
    stmt = sa.update(User). \
        where(User.id == 1). \
        values(name="Alice2"). \
        execution_options(synchronize_session=False)
    ses.execute(stmt)
    print(user.name)
    ses.commit()
    print(user.name)

with orm.Session(engine) as ses:
    user = ses.get(User, 2)
    stmt = sa.update(User). \
        where(User.id == 2). \
        values(name="Bob2"). \
        execution_options(synchronize_session="fetch")
    ses.execute(stmt)
    print(user.name)
    ses.commit()
    print(user.name)

with orm.Session(engine) as ses:
    user = ses.get(User, 3)
    stmt = sa.update(User). \
        where(User.id == 3). \
        values(name="Cathy2"). \
        execution_options(synchronize_session="evaluate")
    ses.execute(stmt)
    print(user.name)
    ses.commit()
    print(user.name)

ses1 = orm.Session(engine)
user = ses.get(User, 4)
stmt = sa.update(User). \
    where(User.id == 4). \
    values(name="David2")
ses1.execute(stmt)
print(user.name)

with orm.Session(engine) as ses2:
    user = ses2.get(User, 4)
    print(user.name)
