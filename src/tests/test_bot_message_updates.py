import asyncio
import json

from sqlalchemy import select

from models import (
    Bot,
    BotRoomAccess,
    BotUpdate,
    Message,
    Room,
    User,
)
from services.message_dispatch import publish_text_message
from ws.manager import manager


def test_message_generates_bot_update(
    session_factory,
    monkeypatch,
):
    Session, _ = session_factory
    broadcasts = []

    async def fake_broadcast(payload, room):
        broadcasts.append((payload, room))

    monkeypatch.setattr(
        manager,
        "broadcast_json",
        fake_broadcast,
    )

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

            access = BotRoomAccess(
                bot_id=bot.id,
                room_id=room.id,
                can_read_messages=True,
                can_send_messages=False,
            )
            db.add(access)
            await db.commit()

            room_id = room.id
            bot_id = bot.id

        # Human message creates an update
        async with Session() as db:
            sent = await publish_text_message(
                db,
                username="alice",
                room="general",
                text="Hello bot!",
            )

            message_id = sent["id"]

        # Read from a new session to verify persistence
        async with Session() as db:
            message = await db.get(Message, message_id)

            updates = (
                await db.scalars(
                    select(BotUpdate).where(
                        BotUpdate.bot_id == bot_id
                    )
                )
            ).all()

            assert message is not None
            assert len(updates) == 1

            event = json.loads(updates[0].payload)

            assert event["message"]["message_id"] == message_id
            assert event["message"]["chat"]["id"] == room_id
            assert event["message"]["text"] == "Hello bot!"
            assert event["message"]["from"]["username"] == "alice"

        # Bot's own message must not create
        # another update for itself
        async with Session() as db:
            await publish_text_message(
                db,
                username="echo_bot",
                room="general",
                text="Hello human!",
            )

        async with Session() as db:
            updates = (
                await db.scalars(
                    select(BotUpdate).where(
                        BotUpdate.bot_id == bot_id
                    )
                )
            ).all()

            assert len(updates) == 1

        assert len(broadcasts) == 2

    asyncio.run(scenario())
