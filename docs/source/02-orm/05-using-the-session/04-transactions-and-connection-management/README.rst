Transactions and Connection Management
==============================================================================

Ref:

- https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html

Using SAVEPOINT
------------------------------------------------------------------------------

SAVEPOINT 是某些 RDBMS 系统上的一中 Feature, 允许你在一个 Transaction 内分多个步骤, 每个步骤都算作一个 nested transaction, 这些 nested transaction 不用 commit, 而用 savepoint 来记录中间状态. 如果有 exception 然后进行 rollback 也不是全部 rollback, 而是 rollback 到上一个 savepoint 处.

Session-level vs. Engine level transaction control
------------------------------------------------------------------------------

Enabling Two-Phase Commit
------------------------------------------------------------------------------
Two Phase Commit (2PC) 是一种分布式一致性协议, 可以让对多个节点写操作要么都完成, 要么都不完成. 该操作主要是对 2 个以上的数据库连接同时进行写操作时用的. 目前 Sqlalchemy 所支持的引擎中有 MySQL, Postgres 支持 2PC.

