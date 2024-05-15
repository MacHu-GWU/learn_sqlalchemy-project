# -*- coding: utf-8 -*-

"""
下面的例子展示了 扩展表的 在 Sqlalchemy 中的实现.

原则:

1. 所有子类都有共同的 primary key column
2. 不要用多重继承! 即一个类只继承一个父类, 不要继承两个以上的父类.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class Company(Base, sam.ExtendedBase):
    __tablename__ = "company"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50))
    employees = orm.relationship("Employee", back_populates="company")
    # engineers = orm.relationship("Engineer", back_populates="company")


class Employee(Base, sam.ExtendedBase):
    __tablename__ = "employee"

    id = sa.Column(sa.Integer, primary_key=True)
    enroll_date = sa.Column(sa.String(50))

    # a special column stores the subclass information
    type = sa.Column(sa.String(50))

    company_id = sa.Column(sa.ForeignKey("company.id"))
    company = orm.relationship("Company", back_populates="employees")

    __mapper_args__ = {
        "polymorphic_identity": "employee",  # the value for type
        "polymorphic_on": type
    }


class Engineer(Employee, sam.ExtendedBase):
    __tablename__ = "engineer"

    id = sa.Column(sa.Integer, sa.ForeignKey("employee.id"), primary_key=True)
    engineer_name = sa.Column(sa.String(30))

    # company_id = sa.Column(sa.ForeignKey("company.id"))
    # company = orm.relationship("Company", back_populates="engineers")

    __mapper_args__ = {
        "polymorphic_identity": "engineer",  # the value for type
    }


class Manager(Employee, sam.ExtendedBase):
    __tablename__ = "manager"

    id = sa.Column(sa.Integer, sa.ForeignKey("employee.id"), primary_key=True)
    manager_name = sa.Column(sa.String(30))

    __mapper_args__ = {
        "polymorphic_identity": "manager",  # the value for type
    }


# 子类的子类
class SoftwareEngineer(Engineer):
    __tablename__ = "software_engineer"

    id = sa.Column(sa.Integer, sa.ForeignKey("engineer.id"), primary_key=True)
    programming_language = sa.Column(sa.String(30))

    __mapper_args__ = {
        "polymorphic_identity": "software_engineer",  # the value for type
    }


class HardwareEngineer(Engineer):
    __tablename__ = "hardware_engineer"

    id = sa.Column(sa.Integer, sa.ForeignKey("engineer.id"), primary_key=True)
    device_platform = sa.Column(sa.String(30))

    __mapper_args__ = {
        "polymorphic_identity": "hardware_engineer",  # the value for type
    }


engine = sam.EngineCreator().create_sqlite()
Base.metadata.create_all(engine)

# 插入一些数据
with orm.Session(engine) as ses:
    company = Company(id=999, name="Google")
    engineer = Engineer(
        id=1,
        enroll_date="2021-01-01",
        company_id=999,
        engineer_name="Alice",
    )
    manager = Manager(
        id=2,
        enroll_date="2021-01-02",
        company_id=999,
        manager_name="Bob",
    )
    software_engineer = SoftwareEngineer(
        id=3,
        enroll_date="2021-01-03",
        company_id=999,
        engineer_name="Cathy",
        programming_language="Python",
    )
    hardware_engineer = HardwareEngineer(
        id=4,
        enroll_date="2021-01-04",
        company_id=999,
        engineer_name="David",
        device_platform="ARM",
    )

    ses.add_all([company, engineer, manager, software_engineer, hardware_engineer])
    ses.commit()

    # 查看子类属性, 以及父类的属性
    engineer = ses.get(Engineer, 1)
    assert engineer.id == 1
    assert engineer.enroll_date == "2021-01-01"
    assert engineer.company.name == "Google"
    assert engineer.type == "engineer"
    assert engineer.engineer_name == "Alice"

    software_engineer = ses.get(SoftwareEngineer, 3)
    assert software_engineer.id == 3
    assert software_engineer.enroll_date == "2021-01-03"
    assert software_engineer.company.name == "Google"
    assert software_engineer.type == "software_engineer"
    assert software_engineer.engineer_name == "Cathy"
    assert software_engineer.programming_language == "Python"

    company = ses.get(Company, 999)
    assert len(company.employees) == 4

with engine.connect() as conn:
    # 查看 Table 中实际储存的数据, 子类的表就只有子类独有属性
    employee = conn.execute(sa.select(Employee.__table__).where(Employee.id == 1)).one()
    assert employee == (1, "2021-01-01", "engineer", 999)
    engineer = conn.execute(sa.select(Engineer.__table__).where(Engineer.id == 1)).one()
    assert engineer == (1, "Alice")

    employee = conn.execute(sa.select(Employee.__table__).where(Employee.id == 3)).one()
    assert employee == (3, "2021-01-03", "software_engineer", 999)
    engineer = conn.execute(sa.select(Engineer.__table__).where(Engineer.id == 3)).one()
    assert engineer == (3, "Cathy")
    software_engineer = conn.execute(sa.select(SoftwareEngineer.__table__).where(SoftwareEngineer.id == 3)).one()
    assert software_engineer == (3, "Python")
