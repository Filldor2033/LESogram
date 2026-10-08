import json
from datetime import timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    Bot,
    BotRoomAccess,
    BotUpdate,
    Message,
    Room,
    User,
)


async def enqueue_message_updates(
    db: AsyncSession,
    *,
    message: Message,
    room: Room,
) -> int:
    """
    Queue a message event for bots with read access.

    Does not commit: caller owns the transaction.
    """

    # Resolve the message author
    sender = await db.scalar(
        select(User).where(
            User.username == message.username
        )
    )

    if sender is None:
        raise ValueError("Message author not found")

    # Find all eligible bot accounts
    result = await db.scalars(
        select(Bot.id)
        .join(
            BotRoomAccess,
            BotRoomAccess.bot_id == Bot.id,
        )
        .join(
            User,
            User.id == Bot.user_id,
        )
        .where(
            BotRoomAccess.room_id == room.id,
            BotRoomAccess.can_read_messages.is_(True),
            Bot.is_active.is_(True),
            User.is_bot.is_(True),
            User.username != sender.username,
        )
    )

    bot_ids = result.all()

    if not bot_ids:
        return 0

    timestamp = message.timestamp

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(
            tzinfo=timezone.utc
        )

    # Bot API event format
    event = {
        "message": {
            "message_id": message.id,
            "date": int(timestamp.timestamp()),
            "chat": {
                "id": room.id,
                "title": room.name,
            },
            "from": {
                "id": sender.id,
                "username": sender.username,
                "is_bot": bool(sender.is_bot),
            },
            "text": message.text or "",
            "reply_to_message_id": message.reply_to_id,
        }
    }

    payload = json.dumps(
        event,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    # Every bot receives its own update record
    db.add_all([
        BotUpdate(
            bot_id=bot_id,
            room_id=room.id,
            update_type="message",
            payload=payload,
        )
        for bot_id in bot_ids
    ])

    return len(bot_ids)


async def discard_bot_room_updates(
    db: AsyncSession,
    *,
    bot_id: int,
    room_id: int,
) -> None:
    """
    Remove all queued events for one bot in one room.

    Does not commit.
    """

    await db.execute(
        delete(BotUpdate).where(
            BotUpdate.bot_id == bot_id,
            BotUpdate.room_id == room_id,
        )
    )
