from datetime import datetime, UTC

from sqlalchemy import Column, Integer, BigInteger, DateTime, Boolean, String

from .connection import Base


class DiscordMessageDeleteTarget(Base):
    __tablename__ = 'discord_message_delete_targets'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordRoomAnnounceTarget(Base):
    __tablename__ = 'discord_room_announce_targets'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordInRoomManager(Base):
    __tablename__ = 'discord_in_room_managers'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    user_id = Column(BigInteger, nullable=False)
    estimated_close_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordRoomAnnounceMessage(Base):
    __tablename__ = 'discord_room_announce_messages'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordThreadCreateNotifyRole(Base):
    __tablename__ = 'discord_thread_create_notify_roles'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    role_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordThreadCreateNotifyIgnoreTarget(Base):
    __tablename__ = 'discord_thread_create_notify_ignore_targets'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=True, default=None)
    category_id = Column(BigInteger, nullable=True, default=None)
    channel_id = Column(BigInteger, nullable=True, default=None)
    thread_id = Column(BigInteger, nullable=True, default=None)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordThreadKeepIgnoreTarget(Base):
    __tablename__ = 'discord_thread_keep_ignore_targets'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=True, default=None)
    category_id = Column(BigInteger, nullable=True, default=None)
    channel_id = Column(BigInteger, nullable=True, default=None)
    thread_id = Column(BigInteger, nullable=True, default=None)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class DiscordThreadTimelineChannel(Base):
    __tablename__ = 'discord_thread_timeline_channels'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    parent_channel_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class TechTrainInviteManagementChannel(Base):
    __tablename__ = 'tech_train_invite_management_channels'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class TechTrainInvite(Base):
    __tablename__ = 'tech_train_invites'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    email = Column(String, nullable=False)
    invite_url = Column(String, nullable=False)

    sender_id = Column(BigInteger, nullable=False)

    is_completed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)


class ReadLaterMessage(Base):
    __tablename__ = 'read_later_message'

    # PK
    id = Column(Integer, primary_key=True)

    # メッセージを保存したユーザー
    user_id = Column(BigInteger, nullable=False)
    # ギルドID
    guild_id = Column(BigInteger, nullable=False)
    # メッセージを保存したチャンネル
    channel_id = Column(BigInteger, nullable=False)
    # メッセージID
    message_id = Column(BigInteger, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)