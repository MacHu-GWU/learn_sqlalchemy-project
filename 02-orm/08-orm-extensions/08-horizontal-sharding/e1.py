# -*- coding: utf-8 -*-

"""
**应用场景**

当数据量变大后, 对数据进行分库分表是平衡数据库流量的常用操作. 好处是将流量分散到各个节点上. 坏处
是查询特别是聚合查询需要将多个结果合并.

**Horizontal Sharding 在 Sqlalchemy 中的实现**

``sqlalchemy.ext.horizontal_shard.ShardedSession`` 提供了一个特殊的 Session, 底层需要
指定多个 engine 的 mapper, 然后提供三个自定义的负载均衡函数:

- shard_chooser: 对 ORM Model 的 instance 进行计算, 决定 shard_id. 比如根据 user.id
    的 hash 值决定单个 shard id. 该操作主要用于 Write 操作.
- id_chooser: 给定一个 identity 的 tuple, 也就是 primary key 的值的 tuple, 哪怕只有
    一个 primary key 也要 pass in 一个 tuple. 决定一个 shard id 的列表. 查询会被路由
    到这些 shards 上然后汇总. 该操作主要用于基于 primary key 的访问.
- execute_chooser: 给定一个 ``sqlalchemy.orm.ORMExecuteState``, 里面会有 select
    statement 的对象, 分析里面的 criterion, 决定一个 shard id 的列表. 查询会被路由到
    这些 shards 上然后汇总. 该操作主要用于复杂 SQL 的查询.
    **注意** 该方法需要对 ``sqlalchemy.orm.ORMExecuteState`` 进行逆向工程, 非常难以实现
    一个完美的方案,

Ref:

- https://docs.sqlalchemy.org/en/latest/orm/extensions/horizontal_shard.html
"""

import random
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, ORMExecuteState
from sqlalchemy.sql import visitors
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.horizontal_shard import ShardedQuery, ShardedSession
import sqlalchemy_mate as sam

engine1 = sam.EngineCreator().create_sqlite()
engine2 = sam.EngineCreator().create_sqlite()
engine3 = sam.EngineCreator().create_sqlite()
engine4 = sam.EngineCreator().create_sqlite()
engine_list = [engine1, engine2, engine3, engine4]

Base = declarative_base()


class User(Base, sam.ExtendedBase):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)


for engine in engine_list:
    Base.metadata.create_all(engine)

shards = {
    str(i): engine
    for i, engine in enumerate(engine_list)
}  # {"0": engine1, "1": engine2, ...}


def get_shard_id_by_user_id(user_id: int) -> str:
    return str(hash(user_id) % 3)


def shard_chooser(
    mapper: dict = None,
    user: User = None,
    clause=None,
) -> str:
    """
    A callable which, passed a Mapper, a mapped instance, and possibly a SQL clause, returns a shard ID. This id may be based off of the attributes present within the object, or on some round-robin scheme. If the scheme is based on a selection, it should set whatever state on the instance to mark it in the future as participating in that shard.
    """
    shard_id = get_shard_id_by_user_id(user.id)
    print("shard_id chosen:", shard_id)
    return shard_id


def id_chooser(
    query,
    identity,
):
    """
    A callable, passed a query and a tuple of identity values, which should return a list of shard ids where the ID might reside. The databases will be queried in the order of this listing.
    """
    chosen_shards = [get_shard_id_by_user_id(identity[0]), ]
    print("id_chooser chosen:", chosen_shards)
    return chosen_shards


def _get_query_comparisons(stmt: Select):
    """
    Search an ``Select`` object for binary expressions.

    Returns expressions which match a Column against one or more
    literal values as a list of tuples of the form
    (column, operator, values).   "values" is a single value
    or tuple of values depending on the operator.
    """
    binds = {}
    clauses = set()
    comparisons = []

    def visit_bindparam(bind):
        # visit a bind parameter.
        value = bind.effective_value
        binds[bind] = value

    def visit_column(column):
        clauses.add(column)

    def visit_binary(binary):
        print(type(binary), binary, binary.left, clauses)
        if binary.left in clauses and binary.right in binds:
            comparisons.append(
                (binary.left, binary.operator, binds[binary.right])
            )

        elif binary.left in binds and binary.right in clauses:
            comparisons.append(
                (binary.right, binary.operator, binds[binary.left])
            )

    # here we will traverse through the query's criterion, searching
    # for SQL constructs.  We will place simple column comparisons
    # into a list.
    if stmt.whereclause is not None:
        visitors.traverse(
            stmt.whereclause,
            {},
            {
                "bindparam": visit_bindparam,
            },
        )
        visitors.traverse(
            stmt.whereclause,
            {},
            {
                "binary": visit_binary,
            },
        )
        visitors.traverse(
            stmt.whereclause,
            {},
            {
                "column": visit_column,
            },
        )
    return comparisons


def execute_chooser(
    query: ORMExecuteState,
):
    """
    For a given ORMExecuteState, returns the list of shard_ids where the query should be issued. Results from all shards returned will be combined together into a single listing.
    """
    # stmt: Select = query.statement
    # comparison = _get_query_comparisons(stmt)
    chosen_shards = list(shards)
    print("execute_chooser chosen", chosen_shards)
    return chosen_shards


with ShardedSession(
    shards=shards,
    shard_chooser=shard_chooser,
    id_chooser=id_chooser,
    # execute_chooser=execute_chooser,
) as ses:
    n_user = 100
    user_list = [
        User(id=i)
        for i in range(1, n_user + 1)
    ]
    random.shuffle(user_list)
    ses.add_all(user_list)
    ses.commit()

    # --- id_chooser
    # get row by primary key will use id_chooser
    print("=== id_chooser example ===")
    user = ses.get(User, 1)
    print(user)

    # --- execute_chooser
    print("=== execute_chooser example ===")
    stmt = sa.select(User).where(User.id == 2)
    # print(ses.execute(stmt).all())
    print(ses.execute(stmt, bind_arguments={"shard_id": get_shard_id_by_user_id(2)}).all())

    # print(sam.pt.from_everything(User, engine1))
    # print(sam.pt.from_everything(User, engine2))
    # print(sam.pt.from_everything(User, engine3))
