import json
from datetime import datetime, timezone

from sqlalchemy import and_, delete, select
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


async def fetch_updates_for_bot(
    db: AsyncSession,
    *,
    bot_id: int,
    expected_token_hash: str,
    offset: int,
    limit: int,
    cleanup_before: datetime | None = None,
    acknowledge: bool = False,
) -> list[dict] | None:
    """
    Fetch pending updates for one bot.

    Returns None if the bot token has been
    revoked or the bot has been disabled.

    Releases the database transaction
    before the next polling iteration.
    """

    # 1. Revalidate bot credentials
    valid_bot_id = await db.scalar(
        select(Bot.id)
        .join(User, User.id == Bot.user_id)
        .where(
            Bot.id == bot_id,
            Bot.token_hash == expected_token_hash,
            Bot.is_active.is_(True),
            User.is_bot.is_(True),
        )
    )

    if valid_bot_id is None:
        await db.rollback()
        return None

    # 2. Delete expired and acknowledged updates
    # Only on the first polling iteration
    if acknowledge:
        if cleanup_before is not None:
            await db.execute(
                delete(BotUpdate).where(
                    BotUpdate.bot_id == bot_id,
                    BotUpdate.created_at < cleanup_before,
                )
            )

        if offset > 0:
            await db.execute(
                delete(BotUpdate).where(
                    BotUpdate.bot_id == bot_id,
                    BotUpdate.id < offset,
                )
            )

        await db.commit()

    # 3. Fetch events with current read permission
    rows = (
        await db.execute(
            select(
                BotUpdate.id,
                BotUpdate.payload,
            )
            .join(
                BotRoomAccess,
                and_(
                    BotRoomAccess.bot_id
                    == BotUpdate.bot_id,
                    BotRoomAccess.room_id
                    == BotUpdate.room_id,
                ),
            )
            .join(
                Bot,
                Bot.id == BotUpdate.bot_id,
            )
            .where(
                BotUpdate.bot_id == bot_id,
                BotUpdate.id >= offset,
                BotRoomAccess.can_read_messages.is_(True),
                Bot.is_active.is_(True),
                Bot.token_hash == expected_token_hash,
            )
            .order_by(BotUpdate.id)
            .limit(limit)
        )
    ).all()

    # 4. Deserialize the stored JSON
    updates = [
        {
            "update_id": update_id,
            **json.loads(raw_payload),
        }
        for update_id, raw_payload in rows
    ]

    # 5. Release the read transaction
    await db.rollback()

    return updates
