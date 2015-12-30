#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.ext.declarative.api import DeclarativeMeta

def one_to_many_insert(session, data, skip_validation=False):
    """在SQLAlchemy的ORM框架中, 为one to many关系进行单一视角Insert的快捷函数。
    """
    # 首先检查输入数据
    if not skip_validation:
        if isinstance(data, list):
            if len(data):
                pass
            else:
                raise ValueError("There's no 'data' to insert!")
        elif isinstance(data.__class__, DeclarativeMeta):
            return one_to_many_insert(session, [data,], skip_validation)
        elif isinstance(data.__class__.__class__, DeclarativeMeta):
            return one_to_many_insert(session, [data,], skip_validation)
        else:
            raise TypeError("'data' is not list type!")
        
    # 然后执行Insert
    for left in data:
        try:
            session.add(left)
            session.commit()
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
    import random, string, time
    
    def rand_str(n=8):
        return "".join(random.sample(string.ascii_letters, n))
    
    # initiate connection
    database = ":memory:"
    engine = create_engine("sqlite:///%s" % database, echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # define one to many schema
    class Department(Base):
        """每一个Department里有多个Employee。
        """
        __tablename__ = "department"
        
        _id = Column(Integer, primary_key=True)
        name = Column(String)
        employees = relationship("Employee", back_populates="department")
        
        def __repr__(self):
            return "Department(_id=%r, name=%r)" % (self._id, self.name)
        
    class Employee(Base):
        """每一个Employee只隶属于一个Department。
        """
        __tablename__ = "employee"
        
        _id = Column(Integer, primary_key=True)
        name = Column(String)
        department_id = Column(Integer, ForeignKey("department._id"))
        
        department = relationship("Department")
        
        def __repr__(self):
            return "Employee(_id=%r, name=%r, department_id=%r)" % (
                self._id, self.name, self.department_id)
        
    Base.metadata.create_all(engine)
    
    # 准备测试数据
    n_employee = 10
    n_department = 4
    all_department = [Department(_id=i, name=rand_str(4)) for i in range(1, 1+n_department)]
    
    # 前十条是正确的数据
    data = list()
    for i in range(1, 1+n_employee):
        employee = Employee(_id=i, name=rand_str(8), 
                            department=random.choice(all_department))
        data.append(employee)
        
    # 后十条是错误的数据, 测试是否当Employee无法插入时, 后续的Department是否
    # 还会被插入(应该是不被插入)
    n_error_employee = 10
    for i in range(n_error_employee):
        employee = Employee(_id=random.randint(1, n_employee), name=rand_str(8),
                            department=Department(_id=random.randint(1, 10), name=rand_str(4)))
        data.append(employee)
    
    # --- apply magic method ---
    one_to_many_insert(session, data)
#     data = Employee(_id=1, name=rand_str(8),
#                     department=random.choice(all_department))
#     one_to_many_insert(session, data)
             
    for department in session.query(Department):
        print(department)
            
    for employee in session.query(Employee):
        print(employee)