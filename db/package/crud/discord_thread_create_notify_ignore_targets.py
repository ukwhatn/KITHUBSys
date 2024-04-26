from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordThreadCreateNotifyIgnoreTarget
# ------


def search_targets(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> list[models.DiscordThreadCreateNotifyIgnoreTarget]:
    return db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(or_(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.category_id == category_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.thread_id == thread_id)).all()


def get_targets_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordThreadCreateNotifyIgnoreTarget]:
    return db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id).all()


def get_target_by_category_id(
        db: Session,
        guild_id: int, category_id: int
) -> models.DiscordThreadCreateNotifyIgnoreTarget | None:
    return db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.category_id == category_id).first()


def get_target_by_channel_id(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordThreadCreateNotifyIgnoreTarget | None:
    return db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.channel_id == channel_id).first()


def get_target_by_thread_id(
        db: Session,
        guild_id: int, thread_id: int
) -> models.DiscordThreadCreateNotifyIgnoreTarget | None:
    return db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.thread_id == thread_id).first()


def create(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> models.DiscordThreadCreateNotifyIgnoreTarget:
    existing = db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.category_id == category_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.thread_id == thread_id).first()

    if existing is not None:
        return existing

    target = models.DiscordThreadCreateNotifyIgnoreTarget(guild_id=guild_id, category_id=category_id,
                                                          channel_id=channel_id, thread_id=thread_id)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def delete(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> None:
    db.query(models.DiscordThreadCreateNotifyIgnoreTarget).filter(
        models.DiscordThreadCreateNotifyIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.category_id == category_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadCreateNotifyIgnoreTarget.thread_id == thread_id).delete()
    db.commit()
