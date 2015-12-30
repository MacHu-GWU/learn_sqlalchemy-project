#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import random, string, time

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
        
    session.commit()

insert_data()

# make query
def select_data():
    for department in session.query(Department):
        print(department, department.employees)
        
    for employee in session.query(Employee):
        print(employee, employee.department)
        
select_data()