#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ORM(object relationship mapping)是一种将类的定义和数据表进行绑定, 然后通过数据库
将类的数据持久化, 同时以面向对象的方式操纵数据库, 或是以数据库的方式对对象进行
查询, 添加, 修改, 删除的技术。

在sqlalchemy中对ORM的操作是通过session来进行的。session是sqlalchemy中的类似于
数据库中transaction的概念, 对session进行的add, update, delete

session.query() and session.execute():

- 使用session.query()进行查询返回的是Object instance。
- 使用session.execute()进行查询返回的是ResultProxy。

filter() and filter_by():

- filter方法使用类名: ``filter(User.name=="Jack")``。
- filter_by方法直接使用列名作为参数, 使用keyword expression。只支持等于操作。
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text)
        
    def __repr__(self):
        return "%s(id=%r, name=%r)" % (
            self.__class__.__name__, self.id, self.name)
        
user_table = User.__table__

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

if __name__ == "__main__":
    from sqlalchemy import select
    
    # --- add some test data --- 
    user = User(id=1, name="Jack")
    session.add(user)
    session.commit()
    
    # --- use query ---
    user = session.query(User).one()
    print(user)
    print(user._asdict())
    
    # --- use execute ---
    row = session.execute(select([user_table])).fetchone()
    print(row)
    
    # --- use filter ---
    print(session.query(User).filter(User.name=="Jack").one())
    
    # --- user filter_by ---
    print(session.query(User).filter_by(name="Jack").one())
    