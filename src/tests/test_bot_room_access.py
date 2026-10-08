import asyncio

import pytest

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import (
    Bot,
    BotRoomAccess,
    Room,
    User,
)


def test_bot_room_access(session_factory):
    Session, _ = session_factory

    async def scenario():
        async with Session() as db:
            owner = User(
                username="alice",
                hashed_password="unused",
            )

            bot_user = User(
                username="echo_bot",
                hashed_password="unused",
                is_bot=True,
            )

            room = Room(
                name="general",
                password_hash="unused",
                created_by="alice",
            )

            db.add_all([owner, bot_user, room])
            await db.flush()

            bot = Bot(
                user_id=bot_user.id,
                owner_id=owner.id,
                token_hash="a" * 64,
            )

            db.add(bot)
            await db.flush()

            # Grant read-only access
            access = BotRoomAccess(
                bot_id=bot.id,
                room_id=room.id,
                can_read_messages=True,
                can_send_messages=False,
            )

            db.add(access)
            await db.commit()

            stored = await db.scalar(
                select(BotRoomAccess).where(
                    BotRoomAccess.bot_id == bot.id
                )
            )

            assert stored is not None
            assert stored.room_id == room.id
            assert stored.can_read_messages is True
            assert stored.can_send_messages is False

            # Cannot add the same bot twice
            db.add(
                BotRoomAccess(
                    bot_id=bot.id,
                    room_id=room.id,
                )
            )

            with pytest.raises(IntegrityError):
                await db.commit()

            await db.rollback()

    asyncio.run(scenario())
