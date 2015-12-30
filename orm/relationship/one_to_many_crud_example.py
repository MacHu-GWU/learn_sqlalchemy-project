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

# insert example
def insert_example():
    """
    模式一: 我们先插入department, 然后插入employee时候指定department_id。
    
    模式二: 我们有一个employee, 并有一个department与其关联。当这个employee的
    primary_key冲突时, 我们应该直接跳过, 对其关联的department部分不做任何更新。
    如果employee的primary_key不冲突, 则对department的primary_key做检查, 如果
    冲突, 是否更新?(通常是不更新, 直接使用) 如果不冲突, 则insert这个department。    
    """
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

    # the real insert
    st = time.clock()
    for employee in data:
        try:
            session.add(employee)
            session.commit()
        except IntegrityError:
            session.rollback()
        except FlushError:
            session.rollback()
             
    print(time.clock() - st)

    for department in session.query(Department):
        print(department)
           
    for employee in session.query(Employee):
        print(employee)
            
# insert_example()

def merge_example():
    """Sqlalchemy给Session提供了一个方法Session.merge(), 可以执行类似于Upsert
    的操作。但是这个操作会对所有的relationship进行update, 即使我们只是需要检查
    relashition是否已被添加, 而不需要对其进行update的情况, 这个操作还是会对所有
    relationship进行update。所以这个简便的语法会带来一定的性能上的问题。
    """
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
    # 还会被插入(应该是不被插入)。在Merge模式下, 由于会采用自动Merge的功能, 
    # 所以当数据中存在primary_key conflict时, 冲突的数据会被update。这就是当
    # 存在错误数据时Merge操作无法完成预期的功能的原因。
#     n_error_employee = 10
#     for i in range(n_error_employee):
#         employee = Employee(_id=random.randint(1, n_employee), name=rand_str(8),
#                             department=Department(_id=random.randint(1, 10), name=rand_str(4)))
#         data.append(employee)

    # the real merge
    st = time.clock()
    for employee in data:
        session.merge(employee)
    session.commit()
    
    print(time.clock() - st)
    
    for department in session.query(Department):
        print(department)
          
    for employee in session.query(Employee):
        print(employee)
        
merge_example()

# update example
def update_example():
    """在ORM中, 对对象做直接修改, 然后执行session.commit(), 即可将修改保存到
    数据库。
    """
    employee = Employee(_id=1, name="Jack", 
                        department=Department(_id=1, name="Finance"))
    session.add(employee)
    session.commit()
     
    employee = session.query(Employee).filter(Employee.department_id==1).one()
    employee.name = "Sam"
    department = employee.department
    department.name = "IT"
    session.commit()
    
    for employee in session.query(Employee):
        print(employee)
    for department in session.query(Department):
        print(department)
    
# update_example()