Column INSERT/UPDATE Defaults
==============================================================================

**Scalar Default**:

.. code-block:: python

    Table("mytable", metadata_obj,
        Column("somecolumn", Integer, default=12)
    )

**Python-Executed Functions**:

.. code-block:: python

    # example 1
    i = 0

    def mydefault():
        global i
        i += 1
        return i

    t = Table("mytable", metadata_obj,
        Column('id', Integer, primary_key=True, default=mydefault),
    )

    # example 2
    import datetime

    t = Table("mytable", metadata_obj,
        Column('id', Integer, primary_key=True),

        # define 'last_updated' to be populated with datetime.now()
        Column('last_updated', DateTime, onupdate=datetime.datetime.now),
    )

**Context-Sensitive Default Functions**:

context 是 Sqlalchemy 独有概念, 是在执行一个 SQL 的时候的上下文数据.

.. code-block:: python

    def mydefault(context):
        return context.get_current_parameters()['counter'] + 12

    t = Table('mytable', metadata_obj,
        Column('counter', Integer),
        Column('counter_plus_twelve', Integer, default=mydefault, onupdate=mydefault)
    )

**Client-Invoked SQL Expressions**:

默认值可以来自于数据库上某个表中的数据或是对其进行的计算.

.. code-block:: python

    t = Table("mytable", metadata_obj,
        Column('id', Integer, primary_key=True),

        # define 'create_date' to default to now()
        Column('create_date', DateTime, default=func.now()),

        # define 'key' to pull its default from the 'keyvalues' table
        Column('key', String(20), default=select(keyvalues.c.key).where(keyvalues.c.type='type1')),

        # define 'last_modified' to use the current_timestamp SQL function on update
        Column('last_modified', DateTime, onupdate=func.utc_timestamp())
    )

**Server-invoked DDL-Explicit Default Expressions**:

默认值可以来自于 服务端 DDL 语言的计算结果, 比如使用数据库系统时间而不是 SQL 客户端的本机时间.

.. code-block:: python

    t = Table('test', metadata_obj,
        Column('abc', String(20), server_default='abc'),
        Column('created_at', DateTime, server_default=func.sysdate()),
        Column('index_value', Integer, server_default=text("0"))
    )

.. code-block:: SQL

    CREATE TABLE test (
        abc varchar(20) default 'abc',
        created_at datetime default sysdate,
        index_value integer default 0
    )

**Marking Implicitly Generated Values, timestamps, and Triggered Columns**:

有些时候默认值在数据库端已经设置了, 计算逻辑和环境都在数据库端部署好了. 此时 Sqlalchemy 可以用 ``FetchedValue`` Mark, 表示这个默认值数据库配置好了, Python 程序你不用管

.. code-block:: python

    from sqlalchemy.schema import FetchedValue

    t = Table('test', metadata_obj,
        Column('id', Integer, primary_key=True),
        Column('abc', TIMESTAMP, server_default=FetchedValue()),
        Column('def', String(20), server_onupdate=FetchedValue())
    )

