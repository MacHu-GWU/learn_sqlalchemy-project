# -*- coding: utf-8 -*-

"""
Department / Employee 是 One-to-Many 的关系.

1. 一个 department 下有很多 employee
2. 一个 employee 隶属于一个 department
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Department(Base, sam.ExtendedBase):
    __tablename__ = "department"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    employees = orm.relationship("Employee", back_populates="department")


class Employee(Base, sam.ExtendedBase):
    __tablename__ = "employee"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    department_id = sa.Column(sa.ForeignKey("department.id"))
    department = orm.relationship(
        "Department",
        # 虽然不是必须的, 但是显式指定总是没错的
        foreign_keys=[department_id, ],
        back_populates="employees",
    )


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

# 插入一些数据
with orm.Session(engine) as ses:
    ses.add_all([
        Department(id=1, name="IT"),
        Department(id=2, name="HR"),
        Employee(id=1, name="Alice", department_id=1),
        Employee(id=2, name="Bob", department_id=1),
        Employee(id=3, name="Cathy", department_id=2),
        Employee(id=4, name="David", department_id=2),
    ])
    ses.commit()

with orm.Session(engine) as ses:
    department: Department = ses.get(Department, 1)
    employee: Employee = ses.get(Employee, 1)
    assert [e.id for e in department.employees] == [1, 2]
    assert employee.department.id == 1

