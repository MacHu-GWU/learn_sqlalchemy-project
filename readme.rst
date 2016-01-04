SQLAlchemy是 "一个知名企业级的持久化模式的，专为高效率和高性能的数据库访问设计的，改编成一个简单的Python域语言的完整套件"。其功能极其完整和强大, 学习曲线对新手可能不够平滑, 但绝对是最值得长期投入学习的库。

此项目是对SQLAlchemy的一些学习笔记和使用案例代码。

其他值得学习的ORM框架:

- peewee: http://docs.peewee-orm.com/en/latest/index.html
	- 优点:
		- Django式的API, 使其易用。
		- 轻量实现, 很容易和任意web框架集成。
	- 缺点:
		- 不支持自动化 schema 迁移。
		- 多对多查询写起来不直观。
- django ORM: django框架自带的ORM, https://docs.djangoproject.com/en/1.9/topics/db/models/
	- 优点:
		- 易用, 学习曲线短。
		- 和Django紧密集合, 用Django时使用约定俗成的方法去操作数据库。
	- 缺点:
		- 不好处理复杂的查询, 强制开发者回到原生SQL。
		- 紧密和Django集成, 使得在Django环境外很难使用。