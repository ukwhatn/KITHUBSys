from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordRoomAnnounceTarget
# ------

def get_targets_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordRoomAnnounceTarget]:
    return db.query(models.DiscordRoomAnnounceTarget).filter(
        models.DiscordRoomAnnounceTarget.guild_id == guild_id).all()


def get_target_by_guild_id_and_channel_id(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordRoomAnnounceTarget | None:
    return db.query(models.DiscordRoomAnnounceTarget).filter(
        models.DiscordRoomAnnounceTarget.guild_id == guild_id,
        models.DiscordRoomAnnounceTarget.channel_id == channel_id).first()


def create(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordRoomAnnounceTarget:
    existing = db.query(models.DiscordRoomAnnounceTarget).filter(
        models.DiscordRoomAnnounceTarget.guild_id == guild_id,
        models.DiscordRoomAnnounceTarget.channel_id == channel_id).first()

    if existing is not None:
        return existing

    target = models.DiscordRoomAnnounceTarget(guild_id=guild_id, channel_id=channel_id)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def delete(
        db: Session,
        guild_id: int, channel_id: int
) -> None:
    db.query(models.DiscordRoomAnnounceTarget).filter(
        models.DiscordRoomAnnounceTarget.guild_id == guild_id,
        models.DiscordRoomAnnounceTarget.channel_id == channel_id).delete()
    db.commit()
