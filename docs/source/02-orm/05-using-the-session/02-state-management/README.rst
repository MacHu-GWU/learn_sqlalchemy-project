State Management
==============================================================================

object 的五种状态
------------------------------------------------------------------------------

    1. Transient, 没有跟 Session 绑定, 也没有被写入 Database, 仅仅是一个被创建的实例.
    2. Pending, 被 Session.add() 添加了, 但还没有被 flush 到 database 中去.
    3. Persistent, 被 flush 到 database 中去了, 或者 commit 之后, session 中的数据和 database 中的数据已经保持一致了.
    4. Deleted, 数据被 Session.delete() 删除, 并已经被 flush 到 database 中去了, 但 transaction 还没有 commit. 和 Pending 刚好是相反的状态.
    5. Detached. 当 delete 被 commit, object 就会从 Session 中移除. 和 Transient 相对应.

获得 object 的状态
------------------------------------------------------------------------------

.. code-block:: python

    from sqlalchemy import inspect
    insp = inspect(my_object)
    insp.persistent

Session Attributes
------------------------------------------------------------------------------
Session 作为 Collection 有点像 Python 中的 Set, 你可以遍历, 或者检查一个 Instance 是否在其中:

.. code-block:: python

    for obj in session:
        print(obj)

    if obj in session:
        print("Object is present")


.. code-block:: python

    # pending objects recently added to the Session
    session.new

    # persistent objects which currently have changes detected
    # (this collection is now created on the fly each time the property is called)
    session.dirty

    # persistent objects that have been marked as deleted via session.delete(obj)
    session.deleted

    # dictionary of all persistent objects, keyed on their
    # identity key
    session.identity_map

Merging
------------------------------------------------------------------------------
