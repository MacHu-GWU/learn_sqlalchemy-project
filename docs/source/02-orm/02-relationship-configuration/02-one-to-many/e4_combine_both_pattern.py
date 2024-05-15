# -*- coding: utf-8 -*-

"""
将 e2, e3 中的例子结合在一起.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Department(Base, sam.ExtendedBase):
    __tablename__ = "department"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    employees = orm.relationship(
        "Employee",
        primaryjoin="Department.id == Employee.department_id",
        back_populates="department",
    )
    devices = orm.relationship("Device", back_populates="department")

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

    department_id = sa.Column(sa.ForeignKey("department.id"))
    department = orm.relationship(
        "Department",
        foreign_keys=[department_id, ],
        back_populates="employees",
    )

    from_department_id = sa.Column(sa.ForeignKey("department.id"))
    from_department = orm.relationship(
        "Department",
        foreign_keys=[from_department_id, ],
        back_populates="about_to_go_employees"
    )

    to_department_id = sa.Column(sa.ForeignKey("department.id"))
    to_department = orm.relationship(
        "Department",
        foreign_keys=[to_department_id, ],
        back_populates="ready_to_join_employees"
    )


class Device(Base, sam.ExtendedBase):
    __tablename__ = "device"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    department_id = sa.Column(sa.ForeignKey("department.id"))
    department = orm.relationship(
        "Department",
        foreign_keys=[department_id, ],
        back_populates="devices"
    )


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

# 插入一些数据
with orm.Session(engine) as ses:
    ses.add_all([
        Department(id=1, name="IT"),
        Department(id=2, name="HR"),
        Employee(
            id=1, name="Alice", department_id=1,
            from_department_id=1, to_department_id=2,
        ),
        Employee(
            id=2, name="Bob", department_id=1,
            from_department_id=1, to_department_id=2,
        ),
        Employee(
            id=3, name="Cathy", department_id=2,
            from_department_id=2, to_department_id=1,
        ),
        Employee(
            id=4, name="David", department_id=2,
            from_department_id=2, to_department_id=1,
        ),
        Device(id=1, name="device A", department_id=1),
        Device(id=2, name="device B", department_id=1),
        Device(id=3, name="device C", department_id=2),
        Device(id=4, name="device D", department_id=2),
    ])
    ses.commit()

with orm.Session(engine) as ses:
    department: Department = ses.get(Department, 1)
    employee: Employee = ses.get(Employee, 1)
    device: Device = ses.get(Device, 1)
    assert [e.id for e in department.employees] == [1, 2]
    assert [e.id for e in department.about_to_go_employees] == [1, 2]
    assert [e.id for e in department.ready_to_join_employees] == [3, 4]
    assert [e.id for e in department.employees] == [1, 2]
    assert [d.id for d in department.devices] == [1, 2]
    assert employee.department.id == 1
    assert device.department.id == 1
