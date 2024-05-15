# -*- coding: utf-8 -*-

"""
Department / Employee 是 One-to-Many 的关系. 但是这里存在不止一组 One-to-Many 关系.

1. Department / Employee.from_department_id
2. Department / Employee.to_department_id

由于存在不止一组关系, 所以在语义上要予以区分.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Department(Base, sam.ExtendedBase):
    __tablename__ = "department"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    about_to_go_employees = orm.relationship(
        "Employee",
        # 显式定义 JOIN 的规则, 这部分是会被 eval() 的, 所以不要用任何变量以防被入侵!
        primaryjoin="Department.id == Employee.from_department_id",
        back_populates="from_department",
    )
    ready_to_join_employees = orm.relationship(
        "Employee",
        # 显式定义 JOIN 的规则, 这部分是会被 eval() 的, 所以不要用任何变量以防被入侵!
        primaryjoin="Department.id == Employee.to_department_id",
        back_populates="to_department",
    )


class Employee(Base, sam.ExtendedBase):
    __tablename__ = "employee"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    from_department_id = sa.Column(sa.ForeignKey("department.id"))
    from_department: Department = orm.relationship(
        "Department",
        # 显式定义具体用哪个 foreign key column
        foreign_keys=[from_department_id, ],
        back_populates="about_to_go_employees",
    )

    to_department_id = sa.Column(sa.ForeignKey("department.id"))
    to_department: Department = orm.relationship(
        "Department",
        # 显式定义具体用哪个 foreign key column
        foreign_keys=[to_department_id, ],
        back_populates="ready_to_join_employees",
    )


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

# 插入一些数据
with orm.Session(engine) as ses:
    ses.add_all([
        Department(id=1, name="IT"),
        Department(id=2, name="HR"),
        Employee(
            id=1, name="Alice",
            from_department_id=1,
            to_department_id=2,
        ),
        Employee(
            id=2, name="Bob",
            from_department_id=1,
            to_department_id=2,
        ),
        Employee(
            id=3, name="Cathy",
            from_department_id=2,
            to_department_id=1,
        ),
        Employee(
            id=4, name="David",
            from_department_id=2,
            to_department_id=1,
        ),
    ])
    ses.commit()

# 测试
with orm.Session(engine) as ses:
    department: Department = ses.get(Department, 1)
    employee: Employee = ses.get(Employee, 1)
    assert [e.id for e in department.about_to_go_employees] == [1, 2]
    assert [e.id for e in department.ready_to_join_employees] == [3, 4]
    assert employee.from_department.id == 1
    assert employee.to_department.id == 2
