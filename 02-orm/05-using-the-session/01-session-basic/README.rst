Session Basic
==============================================================================
.. contents::
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :depth: 1
    :local:


What does the Session do ?
------------------------------------------------------------------------------
Session 中文是会话. 一句话解释就是: "短期存在的一个跟数据库逻辑意义上的连接, 保存着这次交互中所涉及到的所有数据". 我们可以从这么几个方面理解:

1. Session 是逻辑意义上的连接, 不是物理意义上的连接. 要知道跟数据库建立连接的开销要经过多次握手协议, 开销很大. 高频的创建和断开连接不是一个明智的选择. Sqlalchemy 的 engine 在底层维护着一个连接池, 而 Session 则会复用这些连接池. 创建和关闭 Session 实际上是将连接释放回连接池供其他连接使用.
2. Session 在内存中保存着所有 "增删查改" 所涉及到的数据. 当 Write (包括 Insert 和 Update) 还没有被 Commit 到数据库时候, 此时数据是停留在内存中的. 如果在 Commit 或 Session.close() 前进行 Query, 如果可能, Sqlalchemy 会优先使用内存中的数据. Sqlalchemy 用 Identity Map 来维护数据, 简单来说就是一个以 Primary Key 为 Key, Row / Instance 为 Value 的缓存字典. 只有当 Commit 发生时, Session 会将数据 Flush 到数据库. **注意这里涉及到了一个属于 Flush, 其含义是将内存中的数据改变写入数据库**.


Basics of Using a Session
------------------------------------------------------------------------------

**Opening and Closing a Session**

.. code-block:: python

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    # an Engine, which the Session will use for connection
    # resources
    engine = create_engine('postgresql://scott:tiger@localhost/')

    # create session and add objects
    with Session(engine) as session:
        session.add(some_object)
        session.add(some_other_object)
        session.commit()

**Framing out a begin / commit / rollback block**

前面说了 Session 会在内存中维护数据改动. 每次成功 Commit, Session 会记录数据的状态. 如果发生了任何异常, rollback() 方法可以让 Session 回滚到之前成功的 Commit 的数据状态.

下面是一个 Transaction 的例子, 在 begin() 和 commit() 之间的所有操作是原子的 (要么全部成功, 要么全部不成功).

.. code-block:: python

    # verbose version of what a context manager will do
    with Session(engine) as session:
        session.begin()
        try:
            session.add(some_object)
            session.add(some_other_object)
        except:
            session.rollback()
            raise
        else:
            session.commit()

以上的代码等效于:

.. code-block:: python

    # create session and add objects
    with Session(engine) as session:
        with session.begin():
          session.add(some_object)
          session.add(some_other_object)
        # inner context calls session.commit(), if there were no exceptions
    # outer context calls session.close()

最简洁的语法:

.. code-block:: python

    # create session and add objects
    with Session(engine) as session, session.begin():
        session.add(some_object)
        session.add(some_other_object)
    # inner context calls session.commit(), if there were no exceptions
    # outer context calls session.close()

**Using a sessionmaker**

以上的 session 对象是用 ``Session(**kwargs)`` 的方式创建的. sessionmaker 是一种让你每次创建 session 实例的时候无需指定任何参数的方法. sessionmaker 是一个工厂函数, 会用你指定的参数 ``**kwargs`` 创建一个新的Session 类, 这个类不接受任何参数, 所有的参数已经在 sessionmaker 中指定了. 该 Session 和 ``sqlalchemy.orm.Session`` 相似, 但是不是同一个 Session. 前面的那个 Session 是带参数的类, 后一个是不带参数的.

**Expiring / Refreshing**

一个常见的顾虑是, 在你处理一个从 database 中读取而来的对象时, 这些对象的生命周期, 以及他们的状态与数据库中的数据的同步.

Sqlalchemy 使用了一种叫做 Identity Map 的机制. 从数据库中读取的数据都会被 Load 到 Identity Map 中.

- expire: 使一个对象的所有属性过期, 主要是 Lazy Load 来的 foreign key 列所对应的 relationship 的对象.
- refresh: 从数据库中重新读取该对象的属性
- populate_existing: 需要配合 query 使用, 不从 identity map 的缓存中读取任何数据, 全部强制从数据库中读取.

**Selecting a Synchronization Strategy**

所谓同步策略是指

-