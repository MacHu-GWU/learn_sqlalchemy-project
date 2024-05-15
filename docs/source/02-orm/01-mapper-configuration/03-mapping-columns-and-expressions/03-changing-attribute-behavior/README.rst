Changing Attribute Behavior
==============================================================================

这一章讲的主要是在 Attribute 级别进行的自定义. 我们知道对于 Table 而言有很多 Column, 而 Table 对应一个 Class, Column 则对应 Attribute. 在 Python OOP 中有 property, method 之类的概念, 相应的在 SQL 中也有对应的操作. 主要知识点有:

1. Simple Validator: 在创建实例时调用的 validator
2. Descriptors and Hybrids: 详情请参考 :ref:`hybrids` 一章
3. Synonyms: 同义词, 给 Column 定义 Python 级的 alias, 同样可以参与 SQL Expression. hybrids 能做的事情 synonyms 也能做, 不过官方更推荐用 hybrids.
4. Operator Customization: 运算符重载.