#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
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
question_and_tag = Table("question_and_tag", Base.metadata,
    Column("question_id", Integer, ForeignKey("question.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)

class Question(Base):
    """A StackOverFlow question.
    
    每一个Question可能有多个Tag。
    """
    __tablename__ = "question"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, index=True)
    
    tags = relationship("Tag", secondary=question_and_tag,
                        back_populates="questions")
    
    def __repr__(self):
        return "question(id=%r, n_tag=%r)" % (self.id, len(self.tags))
    
class Tag(Base):
    """A question tag.
    
    每一个Tag会被关联到很多个Question上。
    """
    __tablename__ = "tag"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    
    questions = relationship("Question", secondary=question_and_tag,
                             back_populates="tags")
    def __repr__(self):
        return "tag(id=%r, name=%r, n_questions=%r)" % (
            self.id, self.name, len(self.questions))
    
Base.metadata.create_all(engine)

if __name__ == "__main__":
    def initiate_test_data():
        """向数据中插入一些初始数据。
        """
        tag1 = Tag(id=1, name="Python")
        tag2 = Tag(id=2, name="Python2")
        tag3 = Tag(id=3, name="Python3")
        session.add_all([
            Question(id=1, tags=[tag1, tag2]),
            Question(id=2, tags=[tag2, tag3]),
        ])
        session.commit()

    def print_database():
        """打印数据库中的数据。
        """
        for question in session.query(Question):
            print(question)
              
        for tag in session.query(Tag):
            print(tag)
            
    def insert_example():
        """例子: many-to-many关系下的insert操作。
        
        以StackOverFlow社区的发帖为例, 每次你发一个帖子, 下面会提示你输入标签。
        当你输入几个字符后, 系统会提示部分已有的标签。同时你也可以手动输入一个
        新标签。执行插入Question时, 需要到数据库中对所有待插入的Tag进行查询, 
        如果数据库中已经有了, 则使用数据库中的实例, 否则创建一个新实例。
        
        注: 如果数据库中已有``Tag(id=1)``, 那么你定义
        ``question=Question(id=1, tags=[Tag(id=1),]``, 这样做其实是新创建了一个
        实例 ``Tag(id=1)``。所以数据库在执行session.add(question)时, 会出现
        Primary Key Conflict错误。
        """
        # initiate test data
        initiate_test_data()
        
        # add a new question
        question = Question(id=3)
        question.tags = list()
        tag_name_list = ["Python", "Python2", "Python3", "Sqlalchemy"]
        for name in tag_name_list:
            res = session.query(Tag).filter(Tag.name==name).all()
            if len(res) == 1:
                question.tags.append(res[0])
            else:
                question.tags.append(Tag(name=name))
        session.add(question)
        session.commit()
        
        # see if new question and tag been added correctly
        print_database()

#     insert_example()
    
    def merge_example():
        """针对之前insert_example中的例子, sqlalchemy提供了session.merge方法, 能
        简便地insert and update所有关系。
        """
        # initiate test data
        initiate_test_data()
        
        # add a new question
        question = Question(id=3, tags=[
            Tag(id=1, name="Python"),
            Tag(id=2, name="Python2"),
            Tag(id=3, name="Python3"),
            Tag(id=4, name="Sqlalchemy"),
        ])
        session.merge(question)
        session.commit()
        
        # see if new question and tag been added correctly
        print_database()
        
#     merge_example()
    
    def update_example():
        """例子: many-to-many关系下的update操作。
        
        在ORM中, 对对象做直接修改, 然后执行session.commit(), 即可将修改保存到
        数据库。
        """
        # initiate test data
        initiate_test_data()
        
        # update question-tag association
        question = session.query(Question).filter(Question.id==1).one()
        question.tags = [
            session.query(Tag).filter(Tag.id==2).one(),
            session.query(Tag).filter(Tag.id==3).one(),
        ]
        session.commit()
        
        # see if new association data been updated
        print_database()
        
#     update_example()
    
    def delete_question_example():
        """例子: many-to-many关系下的delete操作。
        
        测试当删除一个Question时, 所有与之关联的Tag是否都已被取消关联。
        """
        initiate_test_data()
        
        question = session.query(Question).filter(Question.id==1).one()
        session.delete(question)
        
        # 预期的结果: question1被删除, tag1不再与question1关联
        print_database()
        
#     delete_question_example()
    
    def delete_tag_example():
        """例子: many-to-many关系下的delete操作。
        
        测试当删除一个Tag时, 所有与之关联的Question是否都已被取消关联。
        """
        initiate_test_data()
        
        tag = session.query(Tag).filter(Tag.id==1).one()
        session.delete(tag)
        
        # 预期的结果: tag1被删除, question1不再包含tag1
        print_database()
        
#     delete_tag_example()