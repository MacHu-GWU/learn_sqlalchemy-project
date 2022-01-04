# -*- coding: utf-8 -*-

"""
我们用一个大型互联网公司的热门产品 Youtube 为例, 用 Sqlalchemy 来实现支持 Youtube 运转的关系数据库.
这里面设计了数据关系建模中的各种模式, one-to-many, many-to-many, self-many-to-many, 等等.

**Entities**:

- User: Youtube 用户, 同时也可以是视频创作者.
- Video: 由用户创建的一条视频, 一个视频有且只有一个作者.
- Channel: 一个用户创建的频道, 可以被其他用户 Subscribe. 用户可以把自己创建的视频放到这个频道中. 一个频道可以包含多个视频, 一个视频也可以被多个自己的不同频道所收录.
- PlayList: 一个用户创建的 Playlist, Playlist 的创建者可以把任何无论是别人创建的还是自己的视频加入其中.
- Comment: 一个用户对某一个 Video 的评论留言, 一个 Comment 有且只有一个作者, 且只能跟一个 Video 绑定. 在同一个 Video 下的 Comment 是有严格顺序的.
- Reply: 一个用户对某一个 Comment 的回复. 一个 Reply 有且只有一个作者, 且只能跟一个 Video 绑定. 在同一个 Comment 下的 Reply 时有严格顺序的.

**Relationships**:

- User 和 User 所创建的 Video = One-to-Many. 一个 User 可以创建多个 Video, 一个 Video 只有一个作者.
- User 和 User 所创建的 Channel = One-to-Many. 一个 User 可以创建多个 Channel, 一个 Channel 只有一个作者.
- User 和 User 所创建的 Playlist = One-to-Many. 一个 User 可以创建多个 Playlist, 一个 Playlist 只有一个作者.
- User 和 User 所创建的 Comment = One-to-Many. 一个 User 可以创建多个 Comment, 一个 Comment 只有一个作者.
- User 和 User 所创建的 Reply = One-to-Many. 一个 User 可以创建多个 Reply, 一个 Reply 只有一个作者.
- ``UserAndFollower``, User 和他所 Subscribe 的 User = Many-to-Many. 一个 User 可以 Subscribe 多个 User, 一个 User 也可以被多个 User 所 Subscribe.
- ``ChannelAndFollower``, User 和他所 Subscribe 的 Channel = Many-to-Many. 一个 User 可以 Subscribe 多个 Channel, 一个 Channel 也可以被多个 User 所 Subscribe.
- ``UserAndVideoVote``, User 和他对 Video 的投票. 一个 User 可以对多个 Video 进行投票, 一个 Video 也可以被多个 User 所投票.

- ``ChannelAndItsVideo``, Channel 和 Channel 里包含的 Video = Many-to-Many.
- ``PlaylistAndItsVideo``, Playlist 和 Playlist 里包含的 Video = Many-to-Many.

- Comment 和 Comment 下的 Reply = One-to-Many.
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy_mate as sam

Base = orm.declarative_base()


class ExtendedBase(Base, sam.ExtendedBase):
    __abstract__ = True


# --- Association Tables
class PlayListAndItsVideo(ExtendedBase):
    __tablename__ = "asso_playlist_and_video"

    playlist_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("playlist.playlist_id"),
        primary_key=True,
    )
    video_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("video.video_id"),
        primary_key=True,
    )
    nth = sa.Column(sa.Integer, nullable=False)


class UserAndFollower(ExtendedBase):
    __tablename__ = "asso_user_and_follower"

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


class ChannelAndFollower(ExtendedBase):
    __tablename__ = "asso_channel_and_follower"

    subscriber_user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.user_id"),
        primary_key=True,
    )
    channel_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("channel.channel_id"),
        primary_key=True,
    )


class ChannelAndItsVideo(ExtendedBase):
    __tablename__ = "asso_channel_and_video"

    channel_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("channel.channel_id"),
        primary_key=True,
    )
    video_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("video.video_id"),
        primary_key=True,
    )


class UserAndVideoVote(ExtendedBase):
    __tablename__ = "asso_user_and_video_vote"

    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.user_id"),
        primary_key=True,
    )
    video_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("video.video_id"),
        primary_key=True,
    )
    # 1 = thumb up, 0 = thumb down
    vote = sa.Column(sa.Integer, nullable=False)


# --- Entity Tables
class User(ExtendedBase):
    __tablename__ = "user"

    user_id = sa.Column(sa.Integer, primary_key=True)

    videos = orm.relationship(
        "Video",
        primaryjoin="User.user_id == Video.author_id",
        back_populates="author",
    )
    channels = orm.relationship(
        "Channel",
        primaryjoin="User.user_id == Channel.creator_id",
        back_populates="creator",
    )
    playlists = orm.relationship(
        "Playlist",
        primaryjoin="User.user_id == Playlist.creator_id",
        back_populates="creator",
    )

    subscribed_users = orm.relationship(
        "User",
        secondary=UserAndFollower.__table__,
        primaryjoin=user_id == UserAndFollower.subscriber_user_id,
        secondaryjoin=user_id == UserAndFollower.publisher_user_id,
        back_populates="followers",
    )
    followers = orm.relationship(
        "User",
        secondary=UserAndFollower.__table__,
        primaryjoin=user_id == UserAndFollower.publisher_user_id,
        secondaryjoin=user_id == UserAndFollower.subscriber_user_id,
        back_populates="subscribed_users",
    )

    subscribed_channels = orm.relationship(
        "Channel",
        secondary=ChannelAndFollower.__table__,
        primaryjoin=user_id == ChannelAndFollower.subscriber_user_id,
        back_populates="followers",
    )


class Video(ExtendedBase):
    __tablename__ = "video"

    video_id = sa.Column(sa.Integer, primary_key=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("user.user_id"), nullable=False)
    author = orm.relationship(
        "User",
        foreign_keys=[author_id, ],
        back_populates="videos",
    )

    playlists = orm.relationship(
        "Playlist",
        secondary=PlayListAndItsVideo.__table__,
        back_populates="videos",
    )

    channels = orm.relationship(
        "Channel",
        secondary=ChannelAndItsVideo.__table__,
        primaryjoin=video_id == ChannelAndItsVideo.video_id,
        back_populates="videos",
    )

    thumb_up_count = orm.column_property(
        sa.select(sa.func.count(UserAndVideoVote.user_id)).where(
            UserAndVideoVote.video_id == video_id,
            UserAndVideoVote.vote == 1,
        ).scalar_subquery()
    )

    thumb_down_count = orm.column_property(
        sa.select(sa.func.count(UserAndVideoVote.user_id)).where(
            UserAndVideoVote.video_id == video_id,
            UserAndVideoVote.vote == 0,
        ).scalar_subquery()
    )

    comments = orm.relationship(
        "Comment",
        primaryjoin="Video.video_id == Comment.video_id",
        back_populates="video",
    )


class Channel(ExtendedBase):
    __tablename__ = "channel"

    channel_id = sa.Column(sa.Integer, primary_key=True)
    creator_id = sa.Column(sa.Integer, sa.ForeignKey("user.user_id"), nullable=False)
    creator = orm.relationship(
        "User",
        foreign_keys=[creator_id, ],
        back_populates="channels",
    )

    followers = orm.relationship(
        "User",
        secondary=ChannelAndFollower.__table__,
        primaryjoin=channel_id == ChannelAndFollower.channel_id,
        back_populates="subscribed_channels",
    )

    videos = orm.relationship(
        "Video",
        secondary=ChannelAndItsVideo.__table__,
        primaryjoin=channel_id == ChannelAndItsVideo.channel_id,
        back_populates="channels",
    )


class Playlist(ExtendedBase):
    __tablename__ = "playlist"

    playlist_id = sa.Column(sa.Integer, primary_key=True)
    videos = orm.relationship(
        "Video",
        secondary=PlayListAndItsVideo.__table__,
        back_populates="playlists",
    )

    creator_id = sa.Column(sa.Integer, sa.ForeignKey("user.user_id"), nullable=False)
    creator = orm.relationship(
        "User",
        foreign_keys=[creator_id, ],
        back_populates="playlists",
    )


class Comment(ExtendedBase):
    __tablename__ = "comment"

    video_id = sa.Column(sa.Integer, sa.ForeignKey("video.video_id"), primary_key=True)
    nth_comment = sa.Column(sa.Integer, primary_key=True)

    video = orm.relationship(
        "Video",
        foreign_keys=[video_id, ],
        back_populates="comments",
    )

    author_id = sa.Column(sa.Integer, sa.ForeignKey("user.user_id"), nullable=False)
    author = orm.relationship(
        "User",
        foreign_keys=[author_id, ],
    )

    replies = orm.relationship(
        "Reply",
        primaryjoin="and_(Reply.video_id == Comment.video_id, Reply.nth_comment == Comment.nth_comment)",
        back_populates="comment",
    )


class Reply(ExtendedBase):
    __tablename__ = "reply"

    video_id = sa.Column(sa.Integer, sa.ForeignKey("comment.video_id"), primary_key=True)
    nth_comment = sa.Column(sa.Integer, sa.ForeignKey("comment.nth_comment"), primary_key=True)
    nth_reply = sa.Column(sa.Integer, primary_key=True)

    author_id = sa.Column(sa.Integer, sa.ForeignKey("user.user_id"), nullable=False)

    video = orm.relationship(
        "Video",
        foreign_keys=[video_id, ],
        primaryjoin="Video.video_id == Reply.video_id",
        viewonly=True,
    )

    comment = orm.relationship(
        "Comment",
        foreign_keys=[video_id, nth_comment],
        primaryjoin="and_(Comment.video_id == Reply.video_id, Comment.nth_comment == Reply.nth_comment)",
        back_populates="replies",
    )

    author = orm.relationship(
        "User",
        foreign_keys=[author_id, ],
    )


engine = sam.EngineCreator().create_sqlite()

Base.metadata.create_all(engine)

# --- Data simulator
with orm.Session(engine) as ses:
    ses.add_all([User(user_id=user_id) for user_id in range(1, 10 + 1)])
    ses.commit()

    ses.add_all([
        Video(video_id=1, author_id=1),
        Video(video_id=2, author_id=1),
        Video(video_id=3, author_id=1),
        Video(video_id=4, author_id=1),
        Video(video_id=5, author_id=1),
        Video(video_id=6, author_id=1),
        Video(video_id=7, author_id=1),
        Video(video_id=8, author_id=1),
        Video(video_id=9, author_id=1),
        Video(video_id=10, author_id=1),

        Video(video_id=11, author_id=2),
        Video(video_id=12, author_id=2),
        Video(video_id=13, author_id=2),

        Video(video_id=14, author_id=3),
        Video(video_id=15, author_id=3),
        Video(video_id=16, author_id=3),
        Video(video_id=17, author_id=3),
        Video(video_id=18, author_id=3),

        Video(video_id=19, author_id=4),
        Video(video_id=20, author_id=5),
    ])
    ses.commit()

    ses.add_all([
        Channel(channel_id=1, creator_id=1),
        Channel(channel_id=2, creator_id=1),
        Channel(channel_id=3, creator_id=1),

        Channel(channel_id=4, creator_id=2),

        Channel(channel_id=5, creator_id=3),
        Channel(channel_id=6, creator_id=3),
    ])
    ses.commit()

    ses.add_all([
        ChannelAndItsVideo(channel_id=1, video_id=1),
        ChannelAndItsVideo(channel_id=2, video_id=2),
        ChannelAndItsVideo(channel_id=2, video_id=3),
        ChannelAndItsVideo(channel_id=3, video_id=4),
        ChannelAndItsVideo(channel_id=3, video_id=5),
        ChannelAndItsVideo(channel_id=3, video_id=6),
        ChannelAndItsVideo(channel_id=3, video_id=7),
        ChannelAndItsVideo(channel_id=3, video_id=8),
        ChannelAndItsVideo(channel_id=3, video_id=9),
        ChannelAndItsVideo(channel_id=3, video_id=10),

        ChannelAndItsVideo(channel_id=4, video_id=11),
        ChannelAndItsVideo(channel_id=4, video_id=13),

        ChannelAndItsVideo(channel_id=5, video_id=14),
        ChannelAndItsVideo(channel_id=5, video_id=16),
        ChannelAndItsVideo(channel_id=6, video_id=15),
        ChannelAndItsVideo(channel_id=6, video_id=17),
    ])
    ses.commit()

    ses.add_all([
        UserAndFollower(subscriber_user_id=2, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=3, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=4, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=5, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=6, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=7, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=8, publisher_user_id=1),
        UserAndFollower(subscriber_user_id=9, publisher_user_id=1),

        UserAndFollower(subscriber_user_id=3, publisher_user_id=2),
        UserAndFollower(subscriber_user_id=5, publisher_user_id=2),
        UserAndFollower(subscriber_user_id=7, publisher_user_id=2),
        UserAndFollower(subscriber_user_id=9, publisher_user_id=2),
        UserAndFollower(subscriber_user_id=10, publisher_user_id=2),

        UserAndFollower(subscriber_user_id=6, publisher_user_id=3),
        UserAndFollower(subscriber_user_id=8, publisher_user_id=3),

        UserAndFollower(subscriber_user_id=1, publisher_user_id=4),
        UserAndFollower(subscriber_user_id=2, publisher_user_id=4),
        UserAndFollower(subscriber_user_id=3, publisher_user_id=4),

        UserAndFollower(subscriber_user_id=7, publisher_user_id=5),
        UserAndFollower(subscriber_user_id=8, publisher_user_id=5),
        UserAndFollower(subscriber_user_id=9, publisher_user_id=5),
        UserAndFollower(subscriber_user_id=10, publisher_user_id=5),

        UserAndFollower(subscriber_user_id=6, publisher_user_id=10),
        UserAndFollower(subscriber_user_id=7, publisher_user_id=10),
        UserAndFollower(subscriber_user_id=8, publisher_user_id=10),
    ])
    ses.commit()

    ses.add_all([
        ChannelAndFollower(subscriber_user_id=2, channel_id=1),
        ChannelAndFollower(subscriber_user_id=4, channel_id=1),
        ChannelAndFollower(subscriber_user_id=6, channel_id=1),
        ChannelAndFollower(subscriber_user_id=8, channel_id=1),
        ChannelAndFollower(subscriber_user_id=10, channel_id=1),

        ChannelAndFollower(subscriber_user_id=3, channel_id=2),
        ChannelAndFollower(subscriber_user_id=6, channel_id=2),
        ChannelAndFollower(subscriber_user_id=9, channel_id=2),

        ChannelAndFollower(subscriber_user_id=7, channel_id=3),
        ChannelAndFollower(subscriber_user_id=8, channel_id=3),
        ChannelAndFollower(subscriber_user_id=9, channel_id=3),

        ChannelAndFollower(subscriber_user_id=6, channel_id=6),
        ChannelAndFollower(subscriber_user_id=7, channel_id=6),
        ChannelAndFollower(subscriber_user_id=8, channel_id=6),
        ChannelAndFollower(subscriber_user_id=9, channel_id=6),
        ChannelAndFollower(subscriber_user_id=10, channel_id=6),
    ])
    ses.commit()

    ses.add_all([
        UserAndVideoVote(user_id=6, video_id=1, vote=1),
        UserAndVideoVote(user_id=7, video_id=1, vote=1),
        UserAndVideoVote(user_id=10, video_id=1, vote=1),
        UserAndVideoVote(user_id=9, video_id=1, vote=0),
    ])
    ses.commit()

    ses.add_all([
        Comment(video_id=1, nth_comment=1, author_id=2),
        Comment(video_id=1, nth_comment=2, author_id=3),
        Comment(video_id=1, nth_comment=3, author_id=4),
    ])
    ses.commit()

    ses.add_all([
        Reply(video_id=1, nth_comment=2, nth_reply=1, author_id=9),
        Reply(video_id=1, nth_comment=2, nth_reply=2, author_id=10),
        Reply(video_id=1, nth_comment=3, nth_reply=1, author_id=6),
        Reply(video_id=1, nth_comment=3, nth_reply=2, author_id=7),
        Reply(video_id=1, nth_comment=3, nth_reply=3, author_id=8),
    ])
    ses.commit()

with orm.Session(engine) as ses:
    #--- User ---
    # user: User = ses.get(User, 1)
    # print(f"{user}'s videos: {user.videos}")
    # print(f"{user}'s channels: {user.channels}")
    # print(f"{user}'s playlists: {user.playlists}")
    # print(f"{user}'s follower: {user.followers}")
    #
    # user: User = ses.get(User, 6)
    # print(f"{user} subscribed those users: {user.subscribed_users}")
    # print(f"{user} subscribed those channels: {user.subscribed_channels}")

    #--- Video ---
    # video: Video = ses.get(Video, 1)
    # print(f"{video}'s author: {video.author}")
    # print(f"{video} has {video.thumb_up_count} thumb up")
    # print(f"{video} has {video.thumb_down_count} thumb down")
    # print(f"{video} has those comments: {video.comments}")
    # print(f"{video} belongs to those channels: {video.channels}")
    # print(f"{video} belongs to those playlists: {video.playlists}")

    # --- Comment and Reply ---
    # comment: Comment = ses.get(Comment, (1, 3))
    # print(f"{comment}'s author is {comment.author}")
    # print(f"{comment} belongs to this {comment.video}")
    # print(f"{comment}'s replies: {comment.replies}")
    #
    # reply: Reply = ses.get(Reply, (1, 3, 1))
    # print(f"{reply}'s author is {reply.author}")
    # print(f"{reply} belongs to this {reply.comment}")
    # print(f"{reply} belongs to this {reply.video}")

    # --- DataFrame
    l = [
        User, Video, Channel, Playlist,
        ChannelAndItsVideo, PlayListAndItsVideo,
        UserAndFollower, ChannelAndFollower,
        UserAndVideoVote,
        Comment, Reply,
    ]
    for klass in l:
        print(f"{'=' * 30} {klass.__name__} {'=' * 30}")
        print(sam.pt.from_everything(klass, ses))
