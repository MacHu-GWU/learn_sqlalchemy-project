SQL Expression as Mapped Attributes
==============================================================================

Python 中有一个常见的 getter / setter descriptor: ``@property``. 其作用是定义一个动态计算的类属性. 例如::

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
