from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordThreadCreateNotifyRole
# ------

def get_roles_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.DiscordThreadCreateNotifyRole]:
    return db.query(models.DiscordThreadCreateNotifyRole).filter(
        models.DiscordThreadCreateNotifyRole.guild_id == guild_id).all()


def create(
        db: Session,
        guild_id: int, role_id: int
) -> models.DiscordThreadCreateNotifyRole:
    existing = db.query(models.DiscordThreadCreateNotifyRole).filter(
        models.DiscordThreadCreateNotifyRole.guild_id == guild_id,
        models.DiscordThreadCreateNotifyRole.role_id == role_id).first()

    if existing is not None:
        return existing

    role = models.DiscordThreadCreateNotifyRole(guild_id=guild_id, role_id=role_id)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def delete(
        db: Session,
        guild_id: int, role_id: int
) -> None:
    db.query(models.DiscordThreadCreateNotifyRole).filter(
        models.DiscordThreadCreateNotifyRole.guild_id == guild_id,
        models.DiscordThreadCreateNotifyRole.role_id == role_id).delete()
    db.commit()
