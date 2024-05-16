Lock Row for Update
==============================================================================


Overview
------------------------------------------------------------------------------
在高并发的环境下, 我们要慎重考虑多个 Worker 对同一个 row 进行 Update 的情况. 为了方便说明, 我们将情况简化为 2 个 Worker A 和 B 同时对一个 row update 的情况.

在实际生产环境中, 常见的并发可以分为两种情况.

情况 1: 两个 worker 同时发起了一个 update 操作, 两个操作相差 0.001 秒到达数据库, 而这个 update 操作需要耗时 0.005 秒. 在这种情况下, 数据库引擎内部会将对同一个 row 的两个操作序列化执行. 换言之哪个请求先到就执行哪个, 然后再执行第二个. 这种情况比较简单, 数据库引擎本身就把冲突通过序列化解决了.

情况 2: 在这种情况下, 执行 update 之前我们需要先执行一次 get 获取目前的数据, 然后决定 update 的值应该是什么. 而从 get 到目前的值和真正 update 之间是有一段间隔的, 在这个期间其他人可能会对这个 row 进行 update 并生效, 导致你这个 update 从逻辑上不成立. 在这种情况下我们需要在 Application Code 层面做一些加锁操作进行处理.

本文介绍了如何用 sqlalchemy 正确处理情况 2.


How it Work
------------------------------------------------------------------------------
在现代关系数据库系统中, 通常都会有 ``SELECT FOR UPDATE`` 这一手动加锁的语法. 用户可以用 SELECT 选定一部分 row, 所有被选定的 row 在一个 Transaction 的生命周期内会被加锁, 也就是当你 commit 或是 rollback 后锁才会取消. 这个动作也被称为 "获取锁". 之所以叫它获取锁是因为这个动作是尝试获取锁, 如果不成功 (已经被其他客户端锁住了), 那么用户能选择几种处理方案中的一种. 默认是一直等到这个锁被释放, 也就是自己获得了一把新锁. 你还可以用 ``NOWAIT`` 来选择立刻抛出异常. 你还可以用 ``SKIP LOCKED`` 来自动跳过已经有锁的行.

例如我们在 `postgres 的官方文档中 <https://www.postgresql.org/docs/current/sql-select.html>`_ (查看 ``[ FOR { UPDATE | NO KEY UPDATE | SHARE | KEY SHARE } [ OF table_name [, ...] ] [ NOWAIT | SKIP LOCKED ] [...] ]`` 这一部分) 就可以看到这一语法的详细说明.

在 `sqlalchemy 的官方文档 <https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select.with_for_update>`_ 中我们可以看到这里的关键点有两点:

1. 用 ``with orm.Session().begin():`` 或者类似的语法先创建一个 Transaction 的 context manager.
2. 所有要竞争锁的人用 ``select(...).where(...).with_for_update(nowait=True)`` 语法获取锁. (建议用 no wait, 如果被锁住了则立刻抛出异常, 这适用于大多数情况).

总结一下. ``SELECT ... FOR UPDATE`` 是一种悲观锁的做法. 也就是手动将 row 锁住, 然后再开始干活.


Sample Code
------------------------------------------------------------------------------
下面我们有两个程序, ``select_for_update_1.py`` 扮演先锁住 row 30 秒的程序, ``select_for_update_2.py`` 扮演后来尝试想获取锁的程序.

.. dropdown:: select_for_update_1.py

    .. literalinclude:: ./select_for_update_1.py
       :language: python
       :linenos:

.. dropdown:: select_for_update_2.py

    .. literalinclude:: ./select_for_update_2.py
       :language: python
       :linenos:
