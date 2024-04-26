from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordMessageDeleteTarget
# ------

def get_targets_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordMessageDeleteTarget]:
    return db.query(models.DiscordMessageDeleteTarget).filter(
        models.DiscordMessageDeleteTarget.guild_id == guild_id).all()


def get_target_by_guild_id_and_channel_id(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordMessageDeleteTarget | None:
    return db.query(models.DiscordMessageDeleteTarget).filter(
        models.DiscordMessageDeleteTarget.guild_id == guild_id,
        models.DiscordMessageDeleteTarget.channel_id == channel_id).first()


def create(
        db: Session,
        guild_id: int, channel_id: int
) -> models.DiscordMessageDeleteTarget:
    existing = db.query(models.DiscordMessageDeleteTarget).filter(
        models.DiscordMessageDeleteTarget.guild_id == guild_id,
        models.DiscordMessageDeleteTarget.channel_id == channel_id).first()

    if existing is not None:
        return existing

    target = models.DiscordMessageDeleteTarget(guild_id=guild_id, channel_id=channel_id)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def delete(
        db: Session,
        guild_id: int, channel_id: int
) -> None:
    db.query(models.DiscordMessageDeleteTarget).filter(
        models.DiscordMessageDeleteTarget.guild_id == guild_id,
        models.DiscordMessageDeleteTarget.channel_id == channel_id).delete()
    db.commit()
