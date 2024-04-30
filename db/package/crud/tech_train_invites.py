from sqlalchemy.orm import Session

from .. import models


# ------
# TechTrainInvite
# ------

def get_invites_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.TechTrainInvite]:
    return db.query(models.TechTrainInvite).filter(
        models.TechTrainInvite.guild_id == guild_id).all()


def create(
        db: Session,
        guild_id: int, user_id: int,
        email: str, invite_url: str,
        sender_id: int
) -> models.TechTrainInvite:
    # すべてのパラメータで一意のレコードが存在するか確認
    existing = db.query(models.TechTrainInvite).filter(
        models.TechTrainInvite.guild_id == guild_id,
        models.TechTrainInvite.user_id == user_id,
        models.TechTrainInvite.email == email,
        models.TechTrainInvite.invite_url == invite_url).first()

    if existing is not None:
        return existing

    invite = models.TechTrainInvite(
        guild_id=guild_id, user_id=user_id,
        email=email, invite_url=invite_url, sender_id=sender_id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def complete(
        db: Session,
        invite_id: int
) -> models.TechTrainInvite | None:
    invite = db.query(models.TechTrainInvite).filter(
        models.TechTrainInvite.id == invite_id).first()

    if invite is None:
        return None

    invite.is_completed = True
    db.commit()
    db.refresh(invite)
    return invite
