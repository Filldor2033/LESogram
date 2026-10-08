import asyncio
import json

from sqlalchemy import select

from models import Bot, BotUpdate, Room, User


def test_bot_update_storage(session_factory):
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

            # Create the first update
            first = BotUpdate(
                bot_id=bot.id,
                room_id=room.id,
                update_type="message",
                payload=json.dumps({
                    "message": {
                        "message_id": 100,
                        "chat": {"id": room.id},
                        "text": "Привет!",
                    }
                }, ensure_ascii=False),
            )

            # Create the second update
            second = BotUpdate(
                bot_id=bot.id,
                room_id=room.id,
                update_type="message",
                payload=json.dumps({
                    "message": {
                        "message_id": 101,
                        "chat": {"id": room.id},
                        "text": "Второе сообщение",
                    }
                }, ensure_ascii=False),
            )

            db.add_all([first, second])
            await db.commit()

            updates = (
                await db.scalars(
                    select(BotUpdate)
                    .where(BotUpdate.bot_id == bot.id)
                    .order_by(BotUpdate.id)
                )
            ).all()

            assert len(updates) == 2
            assert updates[0].id < updates[1].id

            data = json.loads(updates[0].payload)

            assert data["message"]["text"] == "Привет!"
            assert data["message"]["chat"]["id"] == room.id
            assert updates[0].update_type == "message"

    asyncio.run(scenario())
