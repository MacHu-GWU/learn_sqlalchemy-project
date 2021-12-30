# -*- coding: utf-8 -*-

"""
Ref:

- https://docs.sqlalchemy.org/en/latest/orm/mapped_sql_expr.html#using-column-property

column_property 和 hybrid_property 很相似. 区别在于 hybrid_property 支持的是
Python 级的属性以及 SQL expression 级的访问, 你在查询返回的结果中这些值不会被计算, 而是
在被访问的时候 (lazy load) 的时候在 runtime 进行计算 (不涉及 DB 查询). 而 column_property
在查询返回的结果中就已经被计算过了.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Address(Base, sam.ExtendedBase):
    __tablename__ = "address"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    address_count = orm.column_property(
        sa.select(sa.func.count(Address.id)).
            where(Address.user_id == id).
            correlate_except(Address).
            scalar_subquery()
    )


engine = sam.EngineCreator().create_sqlite(echo=True)
Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add_all([
        User(id=1),
        User(id=2),
    ])
    ses.add_all([
        Address(id=1, user_id=1),
        Address(id=2, user_id=1),
        Address(id=3, user_id=1),
        Address(id=4, user_id=2),
        Address(id=5, user_id=2),
        Address(id=6, user_id=2),
        Address(id=7, user_id=2),
        Address(id=8, user_id=2),
    ])
    ses.commit()

    user = ses.get(User, 1)
    print(user.address_count)

    stmt = sa.select(User).where(User.address_count == 3)
    res = ses.scalars(stmt).all()
    assert len(res) == 1
    assert res[0].id == 1
    assert res[0].address_count == 3

    print("=" * 80)
    for user in ses.scalars(sa.select(User)):
        print(user, user.address_count)
    # 实际被执行的 SQL 如下
    """
    SELECT 
        user.id,
        (
            SELECT count(address.id) AS count_1 
            FROM address 
            WHERE address.user_id = user.id
        ) AS anon_1 
    FROM user
    """
    