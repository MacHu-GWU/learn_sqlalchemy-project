Describing Databases with MetaData
==============================================================================

Ref:

- https://docs.sqlalchemy.org/en/latest/core/metadata.html

基础知识点
------------------------------------------------------------------------------
1. 创建 metadata container object
2. Declare database table
3. access table from metadata
4. create / drop all tables defined with metadata
5. create / drop individual tables

Specifying the Schema Name
------------------------------------------------------------------------------
很多数据库中都有 Schema 的概念. 它是一个 Name Space 的概念, 相当于一个实体 Database 下的虚拟数据库. 不同 Schema 下的 Table 的名字可以相同. 你可以在用 ``schema`` parameter 来定义 Schema name.

.. code-block:: python

    metadata_obj = MetaData()

    financial_info = Table(
        'financial_info',
        metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('value', String(100), nullable=False),
        schema='remote_banks'
    )

Specifying a Default Schema Name with MetaData
------------------------------------------------------------------------------
当然有更方便的方法, 你可以为 MetaData 指定 default schema, 然后所有与之关联的 Table 如果没有显式指定, 默认就用这个 default schema. 具体语法如下:

.. code-block:: python

    metadata_obj = MetaData(schema="remote_banks")

    financial_info = Table(
        'financial_info',
        metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('value', String(100), nullable=False),
    )

Setting a Default Schema for New Connections
------------------------------------------------------------------------------
