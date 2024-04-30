from sqlalchemy.orm import Session

from .. import models


# ------
# TechTrainInviteManagementChannels
# ------

def get_channels_by_guild_id(
        db: Session,
        guild_id: int
) -> list[models.TechTrainInviteManagementChannel]:
    return db.query(models.TechTrainInviteManagementChannel).filter(
        models.TechTrainInviteManagementChannel.guild_id == guild_id).all()


def create(
        db: Session,
        guild_id: int, channel_id: int
) -> models.TechTrainInviteManagementChannel:
    existing = db.query(models.TechTrainInviteManagementChannel).filter(
        models.TechTrainInviteManagementChannel.guild_id == guild_id,
        models.TechTrainInviteManagementChannel.channel_id == channel_id).first()

    if existing is not None:
        return existing

    channel = models.TechTrainInviteManagementChannel(guild_id=guild_id, channel_id=channel_id)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def delete(
        db: Session,
        guild_id: int, channel_id: int
) -> None:
    db.query(models.TechTrainInviteManagementChannel).filter(
        models.TechTrainInviteManagementChannel.guild_id == guild_id,
        models.TechTrainInviteManagementChannel.channel_id == channel_id).delete()
    db.commit()
