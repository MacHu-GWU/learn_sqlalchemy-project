#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
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

# --- Initiate connection ---
database = ":memory:"
engine = create_engine("sqlite:///%s" % database, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# --- Define schema ---
class Department(Base):
    """每一个Department里有多个Employee。
    """
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    employees = relationship("Employee", back_populates="department")
    
    def __repr__(self):
        return "Department(id=%r, name=%r)" % (self.id, self.name)
    
class Employee(Base):
    """每一个Employee只隶属于一个Department。
    """
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey("department.id"))
    
    department = relationship("Department")
    
    def __repr__(self):
        return "Employee(id=%r, name=%r, department_id=%r)" % (
            self.id, self.name, self.department_id)
    
Base.metadata.create_all(engine)

if __name__ == "__main__":
    def initiate_test_data():
        """向数据中插入一些初始数据。
        """
        department1 = Department(id=1, name="Finance")
        department2 = Department(id=2, name="IT")

        session.add_all([
            Employee(id=1, name="John", department=department1),
            Employee(id=2, name="David", department=department1),
            Employee(id=3, name="Mike", department=department2),
            Employee(id=4, name="Sam", department=department2),
            
        ])
        session.commit()
        
    def print_database():
        """打印数据库中的数据。
        """    
        for employee in session.query(Employee):
            print(employee)
            
        for department in session.query(Department):
            print(department)
            
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
        n_department = 3
        all_department = [Department(id=i, name=rand_str(4)) for i in range(1, 1+n_department)]
        
        # 前十条是正确的数据
        data = list()
        for i in range(1, 1+n_employee):
            employee = Employee(id=i, name=rand_str(8), 
                                department=random.choice(all_department))
            data.append(employee)
            
        # 后十条是错误的数据, 测试是否当Employee无法插入时, 后续的Department是否
        # 还会被插入(应该是不被插入)
        n_error_employee = 10
        for i in range(n_error_employee):
            employee = Employee(id=random.randint(1, n_employee), name=rand_str(8),
                                department=Department(id=random.randint(1, 10), name=rand_str(4)))
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
    
        print_database()
                
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
        all_department = [Department(id=i, name=rand_str(4)) for i in range(1, 1+n_department)]
        
        # 前十条是正确的数据
        data = list()
        for i in range(1, 1+n_employee):
            employee = Employee(id=i, name=rand_str(8), 
                                department=random.choice(all_department))
            data.append(employee)
            
        # 后十条是错误的数据, 测试是否当Employee无法插入时, 后续的Department是否
        # 还会被插入(应该是不被插入)。在Merge模式下, 由于会采用自动Merge的功能, 
        # 所以当数据中存在primary_key conflict时, 冲突的数据会被update。这就是当
        # 存在错误数据时Merge操作无法完成预期的功能的原因。
        n_error_employee = 10
        for i in range(n_error_employee):
            employee = Employee(id=random.randint(1, n_employee), name=rand_str(8),
                                department=Department(id=random.randint(1, 10), name=rand_str(4)))
            data.append(employee)
    
        # the real merge
        st = time.clock()
        for employee in data:
            session.merge(employee)
        session.commit()
        print(time.clock() - st)
        
        print_database()
            
    # merge_example()
    
    def update_example():
        """例子: one-to-many关系下的update操作。
        
        在ORM中, 对对象做直接修改, 然后执行session.commit(), 即可将修改保存到
        数据库。
        """
        employee = Employee(id=1, name="Jack", 
                            department=Department(id=1, name="Finance"))
        session.add(employee)
        session.commit()
         
        employee = session.query(Employee).filter(Employee.department_id==1).one()
        employee.name = "Sam"
        department = employee.department
        department.name = "IT"
        session.commit()
    
        print_database()
        
#     update_example()

    def delete_employee_example():
        """例子: one-to-many关系下的delete操作。
        
        测试当删除一个Employee时, 所有与之关联的Department是否被错误地删除掉了?
        """
        initiate_test_data()
        
        employee = session.query(Employee).filter(Employee.id==1).one()
        session.delete(employee)
        
        print_database()
        
#     delete_employee_example()
    
    def delete_department_example():
        """例子: one-to-many关系下的delete操作。
        
        测试当删除一个Department时, 所有与之关联的Employee是否都已被取消关联。
        """
        initiate_test_data()
        
        department = session.query(Department).filter(Department.id==1).one()
        session.delete(department)
        
        print_database()
        
#     delete_department_example()