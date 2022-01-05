# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlalchemy_mate as sam
from datetime import datetime, timedelta
from learn_sqlalchemy.db import engine_sqlite as engine

metadata = sa.MetaData()

# 先不创建索引
t_event = sa.Table(
    "event", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("time", sa.String),
)

metadata.create_all(engine)

# 先插入一部分数据
start_time = datetime(2000, 1, 1)
data = [
    dict(id=i, time=str((start_time+timedelta(days=i)).date()))
    for i in range(1, 1+500)
]
sam.inserting.smart_insert(engine, t_event, data)

def explain_test_sql(engine):
    with engine.connect() as conn:
        stmt = sa.text("""
        EXPLAIN
        SELECT *
        FROM event
        WHERE
            event.time BETWEEN \"2001-01-01\" AND \"2001-12-31\"
        """)
        res = conn.execute(stmt)
        print(sam.pt.from_result(res))

def run_test_sql(engine):
    with engine.connect() as conn:
        stmt = sa.text("""
        SELECT *
        FROM event
        WHERE
            event.time BETWEEN \"2001-01-01\" AND \"2001-12-31\"
        """)
        res = conn.execute(stmt)
        print(sam.pt.from_result(res))

# Explain 一下 SQL, 发现没有用到 Index
explain_test_sql(engine)

# 创建 Index
index = sa.Index("t_event_c_time", t_event.c.time)
index.create(engine)

# 发现已经用到了 Index
explain_test_sql(engine)
# run_test_sql(engine)

# 再添加多一点数据
data = [
    dict(id=i, time=str((start_time+timedelta(days=i)).date()))
    for i in range(501, 1+1000)
]
sam.inserting.smart_insert(engine, t_event, data)

# 确实用到了 Index
explain_test_sql(engine)
# run_test_sql(engine)