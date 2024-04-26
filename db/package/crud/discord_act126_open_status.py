from datetime import datetime

from sqlalchemy.orm import Session

from .. import models


# ------
# DiscordAct126OpenData
# ------

def cleanup(db: Session) -> list[tuple[int, int, int]]:
    # すべてのデータを削除　-> 毎日22時以降に実行
    messages = db.query(models.DiscordRoomAnnounceMessage).all()
    message_ids = [(message.guild_id, message.channel_id, message.message_id) for message in messages]

    db.query(models.DiscordInRoomManager).delete()
    db.query(models.DiscordRoomAnnounceMessage).delete()

    db.commit()

    return message_ids


def join_room(
        db: Session,
        manager_user_id: int,
        estimated_close_at: datetime,
) -> models.DiscordInRoomManager:
    manager = db.query(models.DiscordInRoomManager).filter(
        models.DiscordInRoomManager.user_id == manager_user_id,
    ).first()

    if manager is None:
        manager = models.DiscordInRoomManager(
            user_id=manager_user_id,
            estimated_close_at=estimated_close_at,
        )
        db.add(manager)
        db.commit()
    else:
        manager.estimated_close_at = estimated_close_at
        db.commit()

    return manager


def leave_room(
        db: Session,
        manager_user_id: int,
) -> list[tuple[int, int, int]] | None:
    db.query(models.DiscordInRoomManager).filter(
        models.DiscordInRoomManager.user_id == manager_user_id,
    ).delete()
    db.commit()

    # managerのデータ数が0になった場合、clean_outdated_dataを実行する
    if db.query(models.DiscordInRoomManager).count() == 0:
        return cleanup(db)

    return None


def add_message(
        db: Session,
        guild_id: int,
        channel_id: int,
        message_id: int,
) -> models.DiscordRoomAnnounceMessage:
    message = models.DiscordRoomAnnounceMessage(
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
    )
    db.add(message)
    db.commit()

    return message


def remove_message(
        db: Session,
        guild_id: int,
        channel_id: int,
        message_id: int,
) -> None:
    db.query(models.DiscordRoomAnnounceMessage).filter(
        models.DiscordRoomAnnounceMessage.guild_id == guild_id,
        models.DiscordRoomAnnounceMessage.channel_id == channel_id,
        models.DiscordRoomAnnounceMessage.message_id == message_id,
    ).delete()
    db.commit()


def get_managers(db: Session) -> list[models.DiscordInRoomManager]:
    return db.query(models.DiscordInRoomManager).all()


def get_messages(db: Session) -> list[models.DiscordRoomAnnounceMessage]:
    return db.query(models.DiscordRoomAnnounceMessage).all()
