SQL Expression as Mapped Attributes
==============================================================================

Python 中有一个常见的 getter / setter descriptor: ``@property``. 其作用是定义一个动态计算的类属性. 例如:

.. code-block:: python

    class User:
        # firstname, lastname 是固有的 attribute
        def __init__(self. firstname: str, lastname: str):
            self.firstname = firstname
            self.lastname = lastname

        # fullname 是动态的 attribute
        @property
        def fullname(self):
            return f"{self.firstname} {self.lastname}"

在 Sqlalchemy ORM 中你当然也可以定义 ``@property``, 不过你无法把这个 property 当成一个 Column 去进行 SQL 查询. 比如你无法用 fullname 作为条件来筛选 User. 为了解决这个问题, 对于那些计算过程比较简单, 可以被 SQL 的内置操作和函数实现的动态 attribute (如果不能被 SQL 内置实现, 那么从逻辑上就不可能实现), Sqlalchemy 允许你定义一个特殊的 property. 在使用上和 ``@property`` 类似, 但是又能参与 SQL 查询.

在 Sqlalchemy 中一共有 4 种定义参与 SQL 运算的 Column 的方法:

1. Hybrid Property: 该 Column 主要作为 WHERE 的条件参与运算, 同时也可以作为一个普通的 property
2. Column Property: 该 Column 在 SQL 执行的时候就返回了, 没有用 Lazy Load. 特别适合无法仅仅从当前 Instance, 而需要依赖其他表的数据才能计算的值. 例如 Count. 因为 Instance 返回过后可能过了很久才需要 Load 这个 Column 的值, 如果用 Lazy Load 可能到时数据的一致性不对.
3. Plain descriptor: 该 Column 作为普通的 property, 但是是一个 SQL Expression 的返回结果. 该 Column 使用了 Lazy Load.
4. Query-time SQL expressions as mapped attributes: 用于你想要返回 Instance 的时候同时返回一些用 SQL Expression 计算出来的计算值. 说白了就是你想在服务器端计算, 而不想在返回 Instance 之后在本地计算.

.. code-block:: python

    class Address(Base):
        __tablename__ = "address"

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey("user.id"))

    class User(Base):
        __tablename__ = "user"

        id = Column(Integer, primary_key=True)
        firstname = Column(String(50))
        lastname = Column(String(50))

        # 1. Hybrid Property
        @hybrid_property
        def fullname(self):
            return self.firstname + " " + self.lastname

        # 2. Column Property
        another_fullname = column_property(firstname + " " + lastname)

        address_count = column_property(
            select(func.count(Address.id)).
            where(Address.user_id==id).
            correlate_except(Address).
            scalar_subquery()
        )

        # 3. Plain descriptor
        @property
        def another_address_count(self):
            return object_session(self).\
                scalar(
                    select(func.count(Address.id)).\
                        where(Address.user_id==self.id)
                )

        # 4. Query-time SQL expressions as mapped attributes
        yet_another_fullname = query_expression()