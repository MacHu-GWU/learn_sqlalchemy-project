# -*- coding: utf-8 -*-

"""
使用SqlAlchemy ORM时, 所有的类都是由 ``declarative_base()`` 继承而来 ``__init__()``方法
也是预定义好了的. 那么当用户想 overwirte 原 ``__init__()``方法时, 就需要用到super关键字,
先执行预定义的 ``__init__()`` 方法, 再执行用户自定义的代码. 具体实现请看例子:
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import sessionmaker
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
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)

    def __init__(self, *args, **kwargs):
        """第一行将所有自带的输入参数传给Base.__init__方法, 保证了原有的行为不变。
        然后接着用户自定义的代码。
        """
        super(User, self).__init__(*args, **kwargs)
        self.classname = self.__class__.__name__


if __name__ == "__main__":
    user = User(id=1, username="jack@gmail.com", password=rand_str(12))
    assert user.classname == "User"
