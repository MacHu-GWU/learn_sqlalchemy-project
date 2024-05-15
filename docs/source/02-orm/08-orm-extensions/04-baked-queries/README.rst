Baked Query
==============================================================================

Ref:

- https://docs.sqlalchemy.org/en/latest/orm/extensions/baked.html

**注意** 1.4 版本开始已经被抛弃了

baked provides an alternative creational pattern for Query objects, which allows for caching of the object’s construction and string-compilation steps. This means that for a particular Query building scenario that is used more than once, all of the Python function invocation involved in building the query from its initial construction up through generating a SQL string will only occur once, rather than for each time that query is built up and executed.

The rationale for this system is to greatly reduce Python interpreter overhead for everything that occurs before the SQL is emitted. The caching of the “baked” system does not in any way reduce SQL calls or cache the return results from the database. A technique that demonstrates the caching of the SQL calls and result sets themselves is available in Dogpile Caching.

简单来说 Baked Query 允许缓存那些使用频率很高的 Query, 使得底层将 Query 转化为底层 SQL 的过程只做一次, 减少了将 Python Query Object 转化为 SQL 在 Python 解释器上的开销. 适合那些常驻内存的应用, 并且频繁执行类似的 Query 的场景. **注意** Baked Query 不会减少 SQL 执行的次数, 也不会缓存任何 Database 返回的结果.
