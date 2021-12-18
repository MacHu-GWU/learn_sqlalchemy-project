#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
很多时候, 我们只希望在数据库中保存几个属性, 而其他的属性可以从这些属性中计算出来。
所以没有必要浪费磁盘。但是我们仅仅定义 ``@property`` 还是不够的, 我们很多情况下都
希望对这些 ``derived`` 属性做查询。这就是 ``hybird_attributes`` 技术所能做到的事。
"""

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func

Base = declarative_base()

class Interval(Base):
    """Interval类, 我们只希望在数据库中保存start和end。其他length, radius都可以
    被计算出来, 所以不需要保存。但是我们有时候希望针对这些项做查询, 例如length。
    所以, 使用 ``hybird_attributes`` 装饰器装饰的类和方法, 可以让这些属性被访问, 
    被调用, 还有最重要的 - 被查询。
    """
    __tablename__ = "interval"

    id = Column(Integer, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @hybrid_property
    def length(self):
        return self.end - self.start

    @hybrid_method
    def contains(self, point):
        return (self.start <= point) & (point <= self.end)

    @hybrid_property
    def radius(self):
        return abs(self.length) / 2

    @radius.expression
    def radius(cls):
        """之前的length, contains之所以能够直接使用filter进行筛选, 是因为计算
        其值的操作都仅仅用到了原生的加减乘除和逻辑运算。如果我们需要更复杂一点
        的运算, 例如求绝对值, 那么我们就需要使用 ``hybrid_property.expression()``
        modifier来对针对该项的查询语句进行定义。
        """
        return func.abs(cls.length) / 2
    
    def __repr__(self):
        return "%s(start=%r, end=%r)" % (
            self.__class__.__name__, self.start, self.end)
    
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

if __name__ == "__main__":
    i1 = Interval(5, 10)
    session.add(i1)
    session.commit()
    
    i = session.query(Interval).filter(Interval.length == 5).one()
    print(i)
    i = session.query(Interval).filter(Interval.contains(8)).one()
    print(i)
    i = session.query(Interval).filter(Interval.radius >= 1).one()
    print(i)
    