from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordThreadKeepIgnoreTarget
# ------
def search_targets(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> list[models.DiscordThreadKeepIgnoreTarget]:
    return db.query(models.DiscordThreadKeepIgnoreTarget).filter(or_(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.category_id == category_id,
        models.DiscordThreadKeepIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadKeepIgnoreTarget.thread_id == thread_id)).all()


def get_targets_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordThreadKeepIgnoreTarget]:
    return db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id).all()


def get_target_by_category_id(
        db: Session,
        guild_id: int, category_id: int
) -> models.DiscordThreadKeepIgnoreTarget | None:
    return db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.category_id == category_id).first()


def get_target_by_channel_id(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordThreadKeepIgnoreTarget | None:
    return db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.channel_id == channel_id).first()


def get_target_by_thread_id(
        db: Session,
        guild_id: int, thread_id: int
) -> models.DiscordThreadKeepIgnoreTarget | None:
    return db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.thread_id == thread_id).first()


def create(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> models.DiscordThreadKeepIgnoreTarget:
    existing = db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.category_id == category_id,
        models.DiscordThreadKeepIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadKeepIgnoreTarget.thread_id == thread_id).first()

    if existing is not None:
        return existing

    target = models.DiscordThreadKeepIgnoreTarget(guild_id=guild_id, category_id=category_id,
                                                  channel_id=channel_id, thread_id=thread_id)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def delete(
        db: Session,
        guild_id: int = None, category_id: int = None, channel_id: int = None, thread_id: int = None
) -> None:
    db.query(models.DiscordThreadKeepIgnoreTarget).filter(
        models.DiscordThreadKeepIgnoreTarget.guild_id == guild_id,
        models.DiscordThreadKeepIgnoreTarget.category_id == category_id,
        models.DiscordThreadKeepIgnoreTarget.channel_id == channel_id,
        models.DiscordThreadKeepIgnoreTarget.thread_id == thread_id).delete()
    db.commit()
