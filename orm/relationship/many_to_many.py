#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
engine = create_engine('sqlite:///%s' % database, echo=False)
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

# insert test data
def insert_data():
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
    for m in session.query(Movie):
        print(m, [m_and_t.tag for m_and_t in m.tags])

    for t in session.query(Tag):
        print(t, [m_and_t.movie for m_and_t in t.movies])
        
select_data()