# -*- coding: utf-8 -*-

"""
**典型用例**

给一个剧院的座椅排位置. 一个厅里有很多排座椅, 一排就是一个 Row, 按照 1,2,3 这样排下去.
每一个 Chair 座椅有独特的编号, 用于追踪座椅的损坏以及库存. 而座椅本身在 Row 中的顺序是
position, 是一个动态值.

``Row.chairs`` 是 ``Chair`` 的列表. 我们希望只管理 列表中 Chair 的元素, 而让 position
属性自动和列表的 index 保持一致.

**该模式在什么情况下会有用?**

"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.ext.orderinglist import ordering_list
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = declarative_base()


class Row(Base, sam.ExtendedBase):
    __tablename__ = "row"

    id = sa.Column(sa.Integer, primary_key=True)

    chairs = relationship(
        "Chair",
        order_by="Chair.id",
        collection_class=ordering_list("position"),
    )


class Chair(Base, sam.ExtendedBase):
    __tablename__ = "chair"

    id = sa.Column(sa.Integer, primary_key=True)
    row_id = sa.Column(sa.Integer, sa.ForeignKey("row.id"))
    position = sa.Column(sa.Integer)


Base.metadata.create_all(engine)

row1 = Row(id=1)
row1.chairs.append(Chair(id=30))
row1.chairs.append(Chair(id=10))
print(row1.chairs)
assert row1.chairs[1].id == 10
assert row1.chairs[1].position == 1

row1.chairs.insert(1, Chair(id=20))
print(row1.chairs)
print(row1.chairs[2])
assert row1.chairs[2].id == 10
assert row1.chairs[2].position == 2

with Session(engine) as ses:
    # state 1
    ses.add(row1)
    ses.commit()
    print(sam.pt.from_everything(Row, ses))
    print(sam.pt.from_everything(Chair, ses))

    # state 2
    # print(dir(row1.chairs))
    row1.chairs.insert(0, Chair(id=40))
    ses.commit()
    print(sam.pt.from_everything(Row, ses))
    print(sam.pt.from_everything(Chair, ses))
