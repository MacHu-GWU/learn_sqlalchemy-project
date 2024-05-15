Column and Data Types
==============================================================================
这一章主要讲的是 Sqlalchemy 自带的各种数据类型.


Generic Types
------------------------------------------------------------------------------
这些是 Python 中的常用数据类型, Sqlalchemy 会自动根据所使用的数据库选择底层的数据类型. SA 保证这些类型可以在任何数据库上使用. 他们都是大写开头, 其他小写.

- ``BigInteger``: A type for bigger int integers.
- ``Boolean``: A bool datatype.
- ``Date``: A type for datetime.date() objects.
- ``DateTime``: A type for datetime.datetime() objects.
- ``Enum``: Generic Enum Type.
- ``Float``: Type representing floating point types, such as FLOAT or REAL.
- ``Integer``: A type for int integers.
- ``Interval``: A type for datetime.timedelta() objects.
- ``LargeBinary``: A type for large binary byte data.
- ``MatchType``: Refers to the return type of the MATCH operator.
- ``Numeric``: A type for fixed precision numbers, such as NUMERIC or DECIMAL.
- ``PickleType``: Holds Python objects, which are serialized using pickle.
- ``SchemaType``: Mark a type as possibly requiring schema-level DDL for usage.
- ``SmallInteger``: A type for smaller int integers.
- ``String``: The base for all string and character types.
- ``Text``: A variably sized string type.
- ``Time``: A type for datetime.time() objects.
- ``Unicode``: A variable length Unicode string type.
- ``UnicodeText``: An unbounded-length Unicode string type

SQL Standard and Multiple Vendor Types
------------------------------------------------------------------------------
这些类型是 SQL 标准的一部分, 也可能是某些数据库上特有的. SA 不保证这些类型能在任何数据库上使用. 他们都是全部大写.

- ``ARRAY``: Represent a SQL Array type.
- ``BIGINT``: The SQL BIGINT type.
- ``BINARY``: The SQL BINARY type.
- ``BLOB``: The SQL BLOB type.
- ``BOOLEAN``: The SQL BOOLEAN type.
- ``CHAR``: The SQL CHAR type.
- ``CLOB``: The CLOB type.
- ``DATE``: The SQL DATE type.
- ``DATETIME``: The SQL DATETIME type.
- ``DECIMAL``: The SQL DECIMAL type.
- ``FLOAT``: The SQL FLOAT type.
- ``INT``: alias of sqlalchemy.sql.sqltypes.INTEGER
- ``INTEGER``: The SQL INT or INTEGER type.
- ``JSON``: Represent a SQL JSON type.
- ``NCHAR``: The SQL NCHAR type.
- ``NUMERIC``: The SQL NUMERIC type.
- ``NVARCHAR``: The SQL NVARCHAR type.
- ``REAL``: The SQL REAL type.
- ``SMALLINT``: The SQL SMALLINT type.
- ``TEXT``: The SQL TEXT type.
- ``TIME``: The SQL TIME type.
- ``TIMESTAMP``: The SQL TIMESTAMP type.
- ``VARBINARY``: The SQL VARBINARY type.
- ``VARCHAR``: The SQL VARCHAR type

Vendor-Specific Types
------------------------------------------------------------------------------
这些是各个数据库独有的特性, 这些类型被储存在 ``sqlalchemy.dialects.${database_system}`` 模块中. 你需要 import 后使用.