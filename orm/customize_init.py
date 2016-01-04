#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用SqlAlchemy ORM时, 所有的类都是由declarative_base()继承而来。__init__()方法
也是预定义好了的。那么当用户想overwirte原__init__()方法时, 就需要用到super关键字
来重写declarative_base()中的方法。具体实现请看例子:
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, noload
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import random, string

def rand_str(n=8):
    return "".join(random.sample(string.ascii_letters + string.digits, n))

# --- Initiate connection ---
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# --- Define schema ---
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    account = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    
    def __init__(self, *args, **kwargs):
        """第一行将所有自带的输入参数传给Base.__init__方法, 保证了原有的行为不变。
        然后接着用户自定义的代码。
        """
        super(User, self).__init__(*args, **kwargs)
        self.classname = self.__class__.__name__
        
    @property
    def password_complexity(self):
        """如果你不想要某个属性一直占用内存, 而仅仅是在需要的时候生成它, 那么
        可以用@property装饰器, 将方法装饰为属性。
        """
        complexity = 1
        for char in "`~!@#$%^&*()_-+={[}]|\:;"'<,>.?/':
            if char in self.password:
                complexity += 1
                break
        for char in string.ascii_uppercase:
            if char in self.password:
                complexity += 1
                break
        for char in string.ascii_lowercase:
            if char in self.password:
                complexity += 1
                break
        for char in string.digits:
            if char in self.password:
                complexity += 1
                break
        return complexity

if __name__ == "__main__":
    user = User(id=1, account="Jack@gmail.com", password=rand_str(12))
    print(user.classname)    
    print(user.password_complexity)