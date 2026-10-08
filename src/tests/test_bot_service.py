import asyncio

import pytest

from auth import hash_password
from models import User
from services.bots import (
    BotUsernameTaken,
    create_bot,
    get_bot_by_token,
    list_owned_bots,
    rotate_bot_token,
    set_bot_active,
)


def test_bot_lifecycle(session_factory):
    Session, _ = session_factory

    async def scenario():
        async with Session() as db:
            owner = User(
                username="alice",
                hashed_password=hash_password("test123"),
            )
            db.add(owner)
            await db.commit()
            await db.refresh(owner)

            bot, token = await create_bot(
                db,
                owner=owner,
                username="echo_bot",
                display_name="Echo Bot",
                description="Test bot",
            )

            assert token.startswith("lsg_")
            assert bot.token_hash != token
            assert bot.owner_id == owner.id
            assert await get_bot_by_token(db, token)

            bots = await list_owned_bots(db, owner.id)
            assert len(bots) == 1
            assert bots[0][1].username == "echo_bot"

            with pytest.raises(BotUsernameTaken):
                await create_bot(
                    db,
                    owner=owner,
                    username="echo_bot",
                    display_name="Duplicate",
                )

            new_token = await rotate_bot_token(
                db,
                owner_id=owner.id,
                bot_id=bot.id,
            )

            assert new_token != token
            assert await get_bot_by_token(db, token) is None
            assert await get_bot_by_token(db, new_token)

            assert await set_bot_active(
                db,
                owner_id=owner.id,
                bot_id=bot.id,
                enabled=False,
            )

            assert await get_bot_by_token(db, new_token) is None

            assert await set_bot_active(
                db,
                owner_id=owner.id,
                bot_id=bot.id,
                enabled=True,
            )

            assert await get_bot_by_token(db, new_token)

    asyncio.run(scenario())
