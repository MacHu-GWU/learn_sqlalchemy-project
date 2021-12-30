# -*- coding: utf-8 -*-

"""
Ref:

- https://docs.sqlalchemy.org/en/latest/orm/mapped_sql_expr.html#using-a-hybrid
- https://docs.sqlalchemy.org/en/latest/orm/extensions/hybrid.html

关于 hybrid attribute 有这么几个基础知识点.

1. 用 hybrid_property 以及 hybrid_method 定义额外的 逻辑 Column, 使之能参与 SQL 的计算.
2. 对于复杂的计算, 用 expression 显示声明在查询时所对应的 SQL
3. 自定义 Setter. 允许用户对这些逻辑 Column 进行修改, 并且修改时对 concrete column 的值
    进行更新. 这里有两种模式, 一个是对 Python 对象的更改, 还有一个是对数据库中的值的更改.

关于进阶知识点请看其他文档.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Interval(Base, sam.ExtendedBase):
    __tablename__ = "interval"

    id = sa.Column(sa.Integer, primary_key=True)
    start = sa.Column(sa.Integer, nullable=False)
    end = sa.Column(sa.Integer, nullable=False)

    # 对于可以用简单的 + - * / > < = & | ! 排列组合的 property
    # 可以直接进行计算, 因为 self.end, self.start 本质上是 column, 这些计算符会有特殊的
    # 含义, 可以被正确地转化为 SQL. 而对于复杂的计算, 你需要用到 sql expression,
    # 详情请参考 radius 部分
    @hybrid_property
    def length(self):
        return self.end - self.start

    # 修改 length 的同时, 也更新 end 的值
    @length.setter
    def length(self, value):
        self.end = self.start + value

    # update length to database, also update end
    @length.update_expression
    def length(cls, value):
        return [
            (cls.end, cls.start + value)  # set cls.end as cls.start + value
        ]

    @hybrid_method
    def contains(self, point):
        return (self.start <= point) & (point <= self.end)

    @hybrid_method
    def intersects(self, other):
        return self.contains(other.start) | self.contains(other.end)

    @hybrid_property
    def radius(self):
        return abs(self.length) / 2

    # 显示告知相对应的 SQL expression
    # 特别注意, 这个 expression 的 name 要和 hybrid_property 的名字一摸一样
    @radius.expression
    def radius(cls):
        return sa.func.abs(cls.length) / 2


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add_all([
        Interval(id=1, start=0, end=10),
        Interval(id=2, start=5, end=15),
        Interval(id=3, start=10, end=20),
        Interval(id=4, start=15, end=30),
    ])
    ses.commit()

    res = ses.scalars(sa.select(Interval).where(Interval.length <= 10)).all()
    print(res)  # id = 1, 2, 3

    res = ses.scalars(sa.select(Interval).where(Interval.contains(7))).all()
    print(res)  # id = 1, 2

    res = ses.scalars(sa.select(Interval).where(Interval.contains(13))).all()
    print(res)  # id = 2, 3

    res = ses.scalars(sa.select(Interval).where(
        Interval.intersects(Interval(id=999, start=7, end=13)))
    ).all()
    print(res)  # id = 1, 2, 3

    res = ses.scalars(sa.select(Interval).where(
        Interval.intersects(Interval(id=999, start=18, end=22)))
    ).all()
    print(res)  # id = 3, 4

    res = ses.scalars(sa.select(Interval).where(Interval.radius < 6)).all()
    print(res)  # id = 1, 2, 3

    res = ses.scalars(sa.select(Interval).where(Interval.radius > 6)).all()
    print(res)  # id = 4

# 更新 length 的同时, end 也被更新了
i = Interval(id=1, start=0, end=10)
i.length = 15
assert i.end == 15

# 更新 length 的同时, end 也被更新了
with orm.Session(engine) as ses:
    ses.add(Interval(id=5, start=0, end=1))
    ses.commit()

    stmt = sa.update(Interval).\
        where(Interval.id == 5).\
        values(length=2).\
        execution_options(synchronize_session="fetch")
    ses.execute(stmt)
    ses.commit()

    i = ses.get(Interval, 5)
    print(i)  # Interval(id=5, start=0, end=2)
