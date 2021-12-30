# -*- coding: utf-8 -*-

"""
Ref:

- https://docs.sqlalchemy.org/en/latest/orm/mapped_sql_expr.html#using-a-hybrid
- https://docs.sqlalchemy.org/en/latest/orm/extensions/hybrid.html

关于 hybrid attribute 有这么几个进阶知识点.

"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import sqlalchemy_mate as sam

Base = orm.declarative_base()
