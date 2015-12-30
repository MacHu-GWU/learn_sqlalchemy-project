#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
import random, string, time

def rand_str(n=8):
    return "".join(random.sample(string.ascii_letters, n))

# initiate connection
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

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

# insert example
def insert_example():
    """
    模式一: 先插入Movie, 再插入Tag, 最后插入MovieAndTag。这种方式是非常简单和
    直观的, 因为三步中任何一步都不太牵扯到其他步骤。
    
    模式二: 我们有一部Movie, 并且有若干个Tag与其关联, 这些Tag可能包含数据库中
    没有的新Tag。这可能是一种比较常见的模式。那么我们就要考虑到如下问题。
    
    1. 这批Tag中哪些在数据库已有对应primary_key的, 是否要对数据库中的Tag进行更新?
      (通常是不要)
    2. 如果Movie有primary_key冲突, 那么已有对应primary_key的Tag要不要更新? 新Tag
      要不要添加? (通常是不要)

    根据以上问题的答案, 我们会有不同的业务逻辑。本例中给出的, 是我们比较常见的
    一种业务逻辑(即答案都是不要)    
    """
    # 准备测试数据
    n_movie = 10
    n_tag = 4
    all_tag = [Tag(_id=i, name=rand_str(4)) for i in range(1, 1+n_tag)]
    
    # 前十条是正确的数据
    data = list()
    for i in range(1, 1+n_movie):
        movie = Movie(_id=i, title=rand_str(8))
        tags = random.sample(all_tag, 2)
        data.append((movie, tags))
        
    # 后十条是错误的数据, 测试是否当Movie无法插入时, 后续的Tag是否还会被插入
    # (应该是不被插入)
    n_error_movie = 10
    for i in range(n_error_movie):
        movie = Movie(_id=random.randint(1, n_movie), title=rand_str(8))
        tags = [Tag(_id=random.randint(1, 10), name=rand_str(4)) for i in range(2)]
        data.append((movie, tags))
    
    # the real insert
    st = time.clock()
    for movie, tags in data:
        try:
            session.add(movie)
            session.commit()
            for tag in tags:
                try:
                    session.add(tag)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                try:
                    movie_and_tag = MovieAndTag(movie_id=movie._id, tag_id=tag._id)
                    session.add(movie_and_tag)
                    session.commit()
                except IntegrityError:
                    session.rollback()
        except IntegrityError:
            session.rollback()
        except FlushError:
            session.rollback()
        
    print(time.clock() - st)
    
    for movie in session.query(Movie):
        print(movie)
         
    for tag in session.query(Tag):
        print(tag)
        
    for movie_and_tag in session.query(MovieAndTag):
        print(movie_and_tag)
        
# insert_example()

# merge example
def merge_exmaple():
    """Sqlalchemy给Session提供了一个方法Session.merge(), 可以执行类似于Upsert
    的操作。但是这个操作会对所有的relationship进行update, 即使我们只是需要检查
    relashition是否已被添加, 而不需要对其进行update的情况, 这个操作还是会对所有
    relationship进行update。所以这个简便的语法会带来一定的性能上的问题。
    """
    # prepare test data
    n_movie = 10
    n_tag = 4
    all_tag = [Tag(_id=i, name=rand_str(4)) for i in range(1, 1+n_tag)]
    
    # 前十条是正确的数据
    data = list()
    for i in range(1, 1+n_movie):
        movie = Movie(_id=i, title=rand_str(8))
        tags = random.sample(all_tag, 2)
        data.append((movie, tags))
        
    # 后十条是错误的数据, 测试是否当Movie无法插入时, 后续的Tag是否还会被插入
    # (应该是不被插入)。在Merge模式下, 由于会采用自动Merge的功能, 所以当数据中
    # 存在primary_key conflict时, 冲突的数据会被update。这就是当存在错误数据时
    # Merge操作无法完成预期的功能的原因。
    total_movie = 10
    for i in range(total_movie):
        movie = Movie(_id=random.randint(1, n_movie), title=rand_str(8))
        tags = [Tag(_id=random.randint(1, 10), name=rand_str(4)) for i in range(2)]
        data.append((movie, tags))
    
    # the real insert
    # 在many to many中, 你无法使用两个类中的任何一个来进行merge
    # 例如假如你要插入一个Movie, 那么就要给定Movie.tags, 但是Movie.tags里的
    # 每一个tag都反过来需要你指定Tag.movies, 这是无法预知的
    st = time.clock()
    for movie, tags in data:
        for movie_and_tag in [
                        MovieAndTag(
                            movie_id=movie._id, tag_id=tag._id,
                            movie=movie, tag=tag
                        ) for tag in tags]:
            session.merge(movie_and_tag)
    session.commit()
    
    print(time.clock() - st)
    
    for movie in session.query(Movie):
        print(movie)
         
    for tag in session.query(Tag):
        print(tag)
        
    for movie_and_tag in session.query(MovieAndTag):
        print(movie_and_tag)
        
# merge_exmaple()

def update_example():
    """请参考one_to_many_crud_example.py中的例子。
    """
    
update_example()