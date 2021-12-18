#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

# --- Initiate connection ---
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# --- Define Schema ---
movie_and_genre = Table("movie_and_genre", Base.metadata,
    Column("movie_id", Integer, ForeignKey("movie.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genre.id"), primary_key=True),
)

person_and_role = Table("person_and_role", Base.metadata,
    Column("person_id", Integer, ForeignKey("person.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
)

movie_and_director = Table("movie_and_director", Base.metadata,
    Column("movie_id", Integer, ForeignKey("movie.id"), primary_key=True),
    Column("director_id", Integer, ForeignKey("person.id"), primary_key=True),
)

movie_and_writer = Table("movie_and_writer", Base.metadata,
    Column("movie_id", Integer, ForeignKey("movie.id"), primary_key=True),
    Column("writer_id", Integer, ForeignKey("person.id"), primary_key=True),
)

movie_and_star = Table("movie_and_star", Base.metadata,
    Column("movie_id", Integer, ForeignKey("movie.id"), primary_key=True),
    Column("star_id", Integer, ForeignKey("person.id"), primary_key=True),
)

class Maker(Base):
    """制作公司。
     
    一个电影只能有一个制作公司, 所以: 电影 to 制作公司 = many to one
    """
    __tablename__ = "maker"
     
    id = Column(Integer, primary_key=True)
    name = Column(String)
     
    movies = relationship("Movie", back_populates="maker")
      
    def __repr__(self):
        return "Maker(id=%r, name=%r, n_movie=%r)" % (self.id, self.name, len(self.movies))
    
class Person(Base):
    """人。
    
    - 一个Person可能有多个Role
    - 一个Person可能导演多个Movie
    - 一个Person可能编剧多个Movie
    - 一个Person可能出演多个Movie
    """
    __tablename__ = "person"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    roles = relationship("Role", secondary=person_and_role,
                         back_populates="persons")
    movies_as_director = relationship("Movie", secondary=movie_and_director,
                                      back_populates="directors")
    movies_as_writer = relationship("Movie", secondary=movie_and_writer,
                                    back_populates="writers")
    movies_as_star = relationship("Movie", secondary=movie_and_star,
                                  back_populates="stars")
    def __repr__(self):
        return "Person(id=%r, name=%r, roles=%r, n_movie_as_director=%r, n_movie_as_writer=%r, n_movie_as_star=%r)" % (
            self.id, self.name, self.roles, 
            len(self.movies_as_director), 
            len(self.movies_as_writer), 
            len(self.movies_as_star),
        )

class Role(Base):
    """人的角色。例如导演, 编剧, 演员。
    
    - 一个Role可能有很多个Person与之关联
    """
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    persons = relationship("Person", secondary=person_and_role,
                           back_populates="roles")
    
    def __repr__(self):
        return "Role(id=%r, name=%r, n_person=%r)" % (
            self.id, self.name, len(self.persons))
        
class Movie(Base):
    """电影。
    
    一部电影可能对应:
    
    - 一个Maker
    - 多个Genre
    - 多个Director
    - 多个Writer
    - 多个Star
    """
    __tablename__ = "movie"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    maker_id = Column(Integer, ForeignKey("maker.id"))
    
    maker = relationship("Maker")
    directors = relationship("Person", secondary=movie_and_director,
                         back_populates="movies_as_director")
    writers = relationship("Person", secondary=movie_and_writer,
                         back_populates="movies_as_writer")
    stars = relationship("Person", secondary=movie_and_star,
                         back_populates="movies_as_star")
    genres = relationship("Genre", secondary=movie_and_genre,
                          back_populates="movies")

    def __repr__(self):
        enter_and_tab = "\n  "
        return "Movie(id=%r, title=%r, %smaker=%r, %sdirectors=%r, %swriters=%r, %sstars=%r, %sgenres=%r,\n)" % (
            self.id, self.title, enter_and_tab, self.maker, 
            enter_and_tab, self.directors, 
            enter_and_tab, self.writers, 
            enter_and_tab, self.stars, 
            enter_and_tab, self.genres)
    
class Genre(Base):
    """电影类型。
    
    - 一个Genre可能有很多个Movie与之关联
    """
    __tablename__ = "genre"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    movies = relationship("Movie", secondary=movie_and_genre,
                          back_populates="genres")
    
    def __repr__(self):
        return "Genre(id=%r, name=%r, n_movie=%r)" % (self.id, self.name, len(self.movies))

Base.metadata.create_all(engine)

# --- unittest ---
if __name__ == "__main__":
    from faker import Factory
    import random
    
    def print_database():
        for movie in session.query(Movie).limit(5):
            print(movie)
    
    def make_fake_data():
        """
        """
        # create fake data
        fake = Factory.create()
        
        #
        role_data = [
            Role(id=1, name="Director"),
            Role(id=2, name="Writer"),
            Role(id=3, name="Star"),
        ]
        
        #
        n_person = 100
        person_data = list()
        for i in range(n_person):
            person_data.append(
                Person(
                    id=i+1, name=fake.name(), 
                    roles=random.sample(role_data, random.randint(1, 3)),
                ) 
            )
            
        #
        director_data, writer_data, star_data = list(), list(), list()
        for person in person_data:
            for role in person.roles:
                if role.id == 1:
                    director_data.append(person)
                elif role.id == 2:
                    writer_data.append(person)
                elif role.id == 3:
                    star_data.append(person)

        #
        maker_list = ["Disney", "Warner", "Dreamworks", "MGM", "Columbia",
            "Revolution", "Artisan", "Newmarket", "Focus Features", "Orion",
            "Gaumont", "Europa Corp", "Show Box", "Constantin Film"]
        maker_data = [Maker(id=i+1, name=name) for i, name in enumerate(maker_list)]
                            
        #
        genre_list = [
            "Actial", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
            "Documentary", "Drama", "Fantasy", "History", "Music", "Mystery", 
            "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western",        
        ]
        genre_data = [Genre(id=i+1, name=name) for i, name in enumerate(genre_list)]
        
        #
        n_movie = 1000
        movie_data = list()
        for i in range(n_movie):
            movie_data.append(
                Movie(
                    id=i+1, title=fake.sentence(),
                    maker=random.choice(maker_data),
                    directors=random.sample(director_data, random.randint(1, 2)),
                    writers=random.sample(writer_data, random.randint(1, 3)),
                    stars=random.sample(star_data, random.randint(2, 5)),
                    genres=random.sample(genre_data, random.randint(1, 3)),                    
                )
            )
            
        # add all data
        session.add_all(maker_data)
        session.add_all(role_data)
        session.add_all(person_data)
        session.add_all(genre_data)
        session.add_all(movie_data)
        session.commit()
        
        # print all data
        print_database()
        
    make_fake_data()