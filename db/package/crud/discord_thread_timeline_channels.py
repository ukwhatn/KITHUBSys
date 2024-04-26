from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordThreadTimelineChannel
# ------

def get_channels_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordThreadTimelineChannel]:
    return db.query(models.DiscordThreadTimelineChannel).filter(
        models.DiscordThreadTimelineChannel.guild_id == guild_id).all()


def get_channels_by_guild_id_and_parent_channel_id(
        db: Session,
        guild_id: int, parent_channel_id: int
) -> list[models.DiscordThreadTimelineChannel]:
    return db.query(models.DiscordThreadTimelineChannel).filter(
        models.DiscordThreadTimelineChannel.guild_id == guild_id,
        models.DiscordThreadTimelineChannel.parent_channel_id == parent_channel_id).all()


def create(
        db: Session,
        guild_id: int, parent_channel_id: int, channel_id: int
) -> models.DiscordThreadTimelineChannel:
    existing = db.query(models.DiscordThreadTimelineChannel).filter(
        models.DiscordThreadTimelineChannel.guild_id == guild_id,
        models.DiscordThreadTimelineChannel.parent_channel_id == parent_channel_id,
        models.DiscordThreadTimelineChannel.channel_id == channel_id).first()

    if existing is not None:
        return existing

    channel = models.DiscordThreadTimelineChannel(guild_id=guild_id, parent_channel_id=parent_channel_id,
                                                  channel_id=channel_id)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def delete(
        db: Session,
        guild_id: int, parent_channel_id: int, channel_id: int
) -> None:
    db.query(models.DiscordThreadTimelineChannel).filter(
        models.DiscordThreadTimelineChannel.guild_id == guild_id,
        models.DiscordThreadTimelineChannel.parent_channel_id == parent_channel_id,
        models.DiscordThreadTimelineChannel.channel_id == channel_id).delete()
    db.commit()
