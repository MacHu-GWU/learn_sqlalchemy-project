# -*- coding: utf-8 -*-

"""
在多对多的关系中有一类比较特殊. 是自己跟自己是多对多的关系. 常见于 图形学, 网络的模型中.
这样的例子很多:

1. Node 作为一个节点. 两个节点之间的连线 Edge 本质上是 Node to Node, 也是多对多的关系.
2. 社交网络上 User 作为一个节点. 一个 User following 另一个 User.
3. 论文数据库的一个 Paper. 一个 Paper 引用另一个 Paper.

知识点:

1. 在 Sqlalchemy 中定义 Self Many to Many 的关系.
2. 定义 Back populates, 从而可以访问以自己为起点的所有终点, 或是以自己为终点的所有起点.
3. 定义一个需要 SQL 查询的特殊属性, 例如以自己为起点的所有边的数量.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam
from learn_sqlalchemy.db import engine_sqlite as engine

Base = orm.declarative_base()


class ExtendedBase(Base, sam.ExtendedBase):
    __abstract__ = True


class UserAndUserSubscription(ExtendedBase):
    __tablename__ = "asso_user_and_subscription"

    subscriber_user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.user_id"),
        primary_key=True,
    )
    publisher_user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.user_id"),
        primary_key=True,
    )


class User(ExtendedBase):
    __tablename__ = "user"

    user_id = sa.Column(sa.Integer, primary_key=True)

    # 定义 relationship
    # secondary = Association Table
    # primaryjoin = 考虑实际的 SQL, 为了得到这一属性, 你需要用到的 JOIN ON 的条件是什么.
    #   这里你为了得到所有你关注的用户, 你需要
    #   UserAndUserSubscription.subscriber_user_id == user_id
    #   这就是 primaryjoin 参数所需要的值
    # secondaryjoin = 另一个 id 的条件
    # back_populates = 另一个属性的名字
    user_i_subscribed = orm.relationship(
        "User",
        secondary=UserAndUserSubscription.__table__,
        primaryjoin=user_id == UserAndUserSubscription.subscriber_user_id,
        secondaryjoin=user_id == UserAndUserSubscription.publisher_user_id,
        back_populates="user_who_subscribe_me",
    )
    user_who_subscribe_me = orm.relationship(
        "User",
        secondary=UserAndUserSubscription.__table__,
        primaryjoin=user_id == UserAndUserSubscription.publisher_user_id,
        secondaryjoin=user_id == UserAndUserSubscription.subscriber_user_id,
        back_populates="user_i_subscribed",
    )

    # 定义 SQL expression 以获得该属性的值.
    _n_user_i_subscribed: int = None

    @property
    def n_user_i_subscribed(self):
        if self._n_user_i_subscribed is None:
            stmt = sa.select(
                sa.func.count(UserAndUserSubscription.publisher_user_id)
            ).where(UserAndUserSubscription.subscriber_user_id == self.user_id)
            self._n_user_i_subscribed = orm.object_session(self).execute(stmt).one()[0]
        return self._n_user_i_subscribed

    _n_follower_cache: int = None

    @property
    def n_follower(self):
        if self._n_follower_cache is None:
            stmt = sa.select(
                sa.func.count(UserAndUserSubscription.subscriber_user_id)
            ).where(UserAndUserSubscription.publisher_user_id == self.user_id)
            self._n_follower_cache = orm.object_session(self).execute(stmt).one()[0]
        return self._n_follower_cache


Base.metadata.create_all(engine)

with orm.Session(engine) as ses:
    ses.add_all([
        User(user_id=1),
        User(user_id=2),
        User(user_id=3),
        User(user_id=4),
    ])
    ses.commit()

    ses.add_all([
        UserAndUserSubscription(subscriber_user_id=1, publisher_user_id=2),
        UserAndUserSubscription(subscriber_user_id=1, publisher_user_id=3),
        UserAndUserSubscription(subscriber_user_id=1, publisher_user_id=4),

        UserAndUserSubscription(subscriber_user_id=2, publisher_user_id=3),
        UserAndUserSubscription(subscriber_user_id=2, publisher_user_id=4),
        UserAndUserSubscription(subscriber_user_id=2, publisher_user_id=1),

        UserAndUserSubscription(subscriber_user_id=3, publisher_user_id=4),
        UserAndUserSubscription(subscriber_user_id=3, publisher_user_id=1),

        UserAndUserSubscription(subscriber_user_id=4, publisher_user_id=1),
        UserAndUserSubscription(subscriber_user_id=4, publisher_user_id=2),
    ])
    ses.commit()

with orm.Session(engine) as ses:
    for user_id in [1, 2, 3, 4]:
        user: User = ses.get(User, user_id)
        print(f"For {user}")
        print("\t", f"I subscribed: {user.user_i_subscribed}")
        print("\t", f"Number of user I subscribed: {user.n_user_i_subscribed}")
        print("\t", f"My followers: {user.user_who_subscribe_me}")
        print("\t", f"Number of user following me: {user.n_follower}")
