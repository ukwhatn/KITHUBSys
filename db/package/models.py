from datetime import datetime, UTC

from sqlalchemy import Column, Integer, BigInteger, DateTime

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
