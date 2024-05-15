# -*- coding: utf-8 -*-

"""
在关系数据库系统中, 一对一, 一对多, 多对一, 多对多的关系是由ForeignKey定义的。
而sqlalchemy的Relationship Loading Technique可以让你在读取一个表时, 自动读取
另一个表中相关联的数据。而这一过程是由在对象中定义一个relationship的列来实现的。

在下面的测试中, 有一个one-to-many的Department-to-Employee的例子, 和many-to-many的
Movie-to-Tag的例子。

起初笔者认为, 由于如果要读取其他表的数据, 是要消耗额外的资源的。所以笔者使用
noload关键字替换掉默认的lazyload, 结果发现。这一过程如果没有Commit, noload要比
lazyload快; 而如果Commit了, 两者需要的时间基本相同。所以笔者认为, sqlalchemy
默认采取了一种策略, 只要你定义了relationship, 无论你load不load, 后台都将其缓存
在某个地方了。区别只不过是, noload的话仅仅在你需要的时候load。

而且笔者还发现, 即使取消relationship的定义, 读取数据的时间也并没有变慢多少。说明
sqlalchemy采用了非常高性能的算法进行笛卡尔运算, 使得relationship loading非常迅速。

结论: ORM的relationship功能, 可以忽略性能损失, 放心使用。

ref: http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#sqlalchemy.orm.lazyload
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, noload
from sqlalchemy.orm import sessionmaker
import random, string, time

def rand_str(n=8):
    return "".join(random.sample(string.ascii_letters, n))

# --- Initiate connection ---
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# --- Define one to many schema ---
class Department(Base):
    """每一个Department里有多个Employee。
    """
    __tablename__ = "department"
    
    _id = Column(Integer, primary_key=True)
    
    employees = relationship("Employee", back_populates="department")
    
    def __repr__(self):
        return "Department(_id=%r)" % self._id
    
class Employee(Base):
    """每一个Employee只隶属于一个Department。
    """
    __tablename__ = "employee"
    
    _id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("department._id"))
    
    department = relationship("Department")
    
    def __repr__(self):
        return "Employee(_id=%r, department_id=%r)" % (self._id, self.department_id)

# define many to many schema
class Movie(Base):
    """每一个Movie有若干个Tag。
    """
    __tablename__ = "movie"
    
    _id = Column(Integer, primary_key=True)
    title = Column(String)
    
    tags = relationship("MovieAndTag", back_populates="movie")
    
    def __repr__(self):
        return "Movie(_id=%r, title=%r)" % (self._id, self.title)

class Tag(Base):
    """每一个Tag被若干个Movie包含了。
    """
    __tablename__ = "tag"
    
    _id = Column(Integer, primary_key=True)
    name = Column(String)
    
    movies = relationship("MovieAndTag", back_populates="tag")

    def __repr__(self):
        return "Tag(_id=%r, name=%r)" % (self._id, self.name)

class MovieAndTag(Base):
    """Movie和Tag的相互关系
    """
    __tablename__ = "movie_and_tag"
    
    movie_id = Column(Integer, ForeignKey("movie._id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag._id"), primary_key=True)
    
    movie = relationship("Movie", back_populates="tags")
    tag = relationship("Tag", back_populates="movies")
    
    def __repr__(self):
        return "MovieAndTag(movie_id=%r, tag_id=%r)" % (self.movie_id, self.tag_id)

Base.metadata.create_all(engine)

# insert test data
def insert_data():
    n_of_department = 10
    n_of_employee = 1000
    
    for i in range(n_of_department):
        department = Department(_id=i)
        session.add(department)
        
    for i in range(n_of_employee):
        employee = Employee(_id=i, 
                            department_id=random.choice(range(n_of_department)))
        session.add(employee)
    
    n_movie = 1000
    n_tag = 20
    n_tag_per_movie = 5
    
    for i in range(n_movie):
        movie = Movie(_id=i, title=rand_str(10))
        session.add(movie)
        
    for i in range(n_tag):
        tag = Tag(_id=i, name=rand_str(4))
        session.add(tag)
        
    for i in range(n_movie):
        for j in random.sample(range(n_tag), n_tag_per_movie):
            movie_and_tag = MovieAndTag(movie_id=i, tag_id=j)
            session.add(movie_and_tag)
    
    session.commit()
    
insert_data()

# make query
def select_data():
    # department and employee
    st = time.clock()
    for d in session.query(Department):
#         print(d, d.employees)
        pass
    print("Select Department lazyload takes %.6f sec." % (time.clock() - st, ))
    
    st = time.clock()
    for d in session.query(Department).options(noload("employees")):
#         print(d, d.employees)
        pass
    print("Select Department noload takes %.6f sec." % (time.clock() - st, ))
    
    # movie and tag
    st = time.clock()
    for m in session.query(Movie):
        print(m, m.tags)
        pass
    print("Select Movie lazyload takes %.6f sec." % (time.clock() - st, ))
    
    st = time.clock()
    for m in session.query(Movie).options(noload("tags")):
#         print(m, m.tags)
        pass
    print("Select Movie noload takes %.6f sec." % (time.clock() - st, ))
       
select_data()