#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.ext.declarative.api import DeclarativeMeta

def many_to_many_insert(session, data, association_cls, skip_validation=False):
    """在SQLAlchemy的ORM框架中, 为many to many关系进行单一视角Insert的快捷函数。
    """
    # 首先检查输入数据
    if not skip_validation:
        if isinstance(data, list):
            if len(data):
                if isinstance(data[0], tuple):
                    pass
                else:
                    raise TypeError("Items in 'data' has to be tuple!")
            else:
                raise ValueError("There's no 'data' to insert!")
        elif isinstance(data, tuple):
            return many_to_many_insert(session, [data,], association_cls, 
                                       skip_validation)
        else:
            raise TypeError("'data' is not list type!")

    
    # 接着取出left表的primary_key column的全名
    left, right_list = data[0]
    left_primary_key_column_list = list(left.__table__.primary_key)
    if len(left_primary_key_column_list) != 1:
        raise Exception
    left_primary_key_column = left_primary_key_column_list[0]
    
    # 然后分析Association Class对应的Table
    # 1. 找到两个primary key column
    # 2. 找到两个primary key column所对应的foreign key
    # 3. 比较两个foreign key column, 找出哪个是left, 哪个是right
    # 4. 找到left和right表的primary key
    primary_key_column_list = list(association_cls.__table__.primary_key)
    if len(primary_key_column_list) == 2:
        col1, col2 = primary_key_column_list
        if (len(col1.foreign_keys) == 1 & len(col2.foreign_keys) == 1):
            col1_primary_key_column = list(col1.foreign_keys)[0].column
            col2_primary_key_column = list(col2.foreign_keys)[0].column
            if col1_primary_key_column is left_primary_key_column:
                left_association_key = col1.name
                left_primary_key = left_primary_key_column.name
                right_association_key = col2.name
                right_primary_key = col2_primary_key_column.name
            elif col2_primary_key_column is left_primary_key_column:
                left_association_key = col2.name
                left_primary_key = col2_primary_key_column.name
                right_association_key = col1.name
                right_primary_key = left_primary_key_column.name
            else:
                raise Exception("Unable to find left/right primary key") # TODO
        else:
            raise Exception("The two primary key column in 'association' table "
                            "don't exactly have one foreign key!")
    else:
        raise Exception("The 'association' table doesn't have "
                        "two primary key column!")
        
    # 最后执行Insert
    for left, right_list in data:
        try:
            session.add(left)
            session.commit()
            for right in right_list:
                try:
                    session.add(right)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                try:
                    kwargs = {
                        left_association_key: left.__getattribute__(left_primary_key),
                        right_association_key: right.__getattribute__(right_primary_key),
                    }
                    association = association_cls(**kwargs)
                    session.add(association)
                    session.commit()
                except IntegrityError:
                    session.rollback()
        except IntegrityError:
            session.rollback()
        except FlushError:
            session.rollback()
            
if __name__ == "__main__":
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import create_engine
    from sqlalchemy import Column
    from sqlalchemy import Integer, String, ForeignKey
    from sqlalchemy.orm import relationship
    from sqlalchemy.orm import sessionmaker
    import random, string

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
    
    # --- apply magic method ---
    many_to_many_insert(session, data, MovieAndTag)
#     data = (Movie(_id=1, title=rand_str(8)), random.sample(all_tag, 2))
#     many_to_many_insert(session, data, MovieAndTag)
        
    for movie in session.query(Movie):
        print(movie)
           
    for tag in session.query(Tag):
        print(tag)
          
    for movie_and_tag in session.query(MovieAndTag):
        print(movie_and_tag)