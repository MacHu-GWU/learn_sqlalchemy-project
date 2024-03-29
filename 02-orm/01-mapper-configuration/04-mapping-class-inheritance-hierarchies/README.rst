Mapping Class Inheritance Hierarchies
==============================================================================
熟悉 "继承在 ORM 中的实现" 的人会知道, 通常有三种实现方法.

**1. 单表继承 (Single Table Inheritance)**.

简单来说就是一个表的所有的列是所有父类和子类的属性的并集(总和), 从表的角度看就是这样::

    person
    |--- name: str
    |--- student_program: str
    |--- teacher_department: str
    ...

优点就是简单, 缺点就是对于很多对象是用不到很多列的, 会造成很多列是 NULL, 造成存储浪费. 并且可能最后由于子类的变种很多, 最后一个表有几百列, 难以管理, 甚至达到了数据库的上限.

在该实现中如果你从数据库直接查询一个行而不是通过 ORM 框架查, 你是不知道这一行到底是哪个类的. 所以通常我们会预留一个特殊的列用来表示这一行到底是属于哪个类.

适用场景: 类的总数不多, 总行数不多, 继承扩展的属性不多的情况.

**2. 扩展表 (Class Table Inheritance)**.

每个类单独创建一个表. 例如 ``person``, ``person_student``, ``person_teacher``. 但是每个表只保存他与父类相比多出来的那些列 以及 foreign key 的列.

优点是节约空间, 没有冗余. 缺点是为了查询一个对象, 需要用到 JOIN, 如果是单个继承则是 1 个 JOIN, 如果是多重继承则是多个 JOIN.

适用场景: 继承体系复杂, 结构容易变, 最大程度减少数据冗余的情景.

**3. 实体表 (Concrete Table Inheritance)**.

每个类单独一个表, 并且保存该类的全部属性, 包括父类中的属性. 本质上各个类从数据库的角度看并没有关联, 在数据库迁徙的时候会比较容易, 缺点就是冗余量非常大.

适用场景: 继承关系不复杂, 查询性能要求高, 父类属性少, 子类属性多的情况.

Reference:

- https://cloud.tencent.com/developer/article/1026510
