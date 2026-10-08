import asyncio
import json
from datetime import timedelta

from models import BotUpdate
from tests.helpers import register
from utils.time import utc_now


def test_get_updates(client, session_factory):
    owner = register(client, "alice")

    room_response = client.post(
        "/api/rooms",
        headers=owner,
        json={
            "name": "general",
            "password": "roompass",
        },
    )
    assert room_response.status_code == 200
    room_id = room_response.json()["room_id"]

    created = client.post(
        "/api/bots",
        headers=owner,
        json={
            "username": "echo_bot",
            "display_name": "Echo Bot",
        },
    )
    assert created.status_code == 201

    bot = created.json()
    bot_id = bot["id"]

    headers = {
        "Authorization": f"Bot {bot['token']}"
    }

    added = client.post(
        f"/api/rooms/{room_id}/bots",
        headers=owner,
        json={
            "username": "echo_bot",
            "can_read_messages": True,
        },
    )
    assert added.status_code == 201

    url = "/api/bot/getUpdates"

    # Authentication
    assert client.post(
        url, json={}
    ).status_code == 401

    assert client.post(
        url, headers=owner, json={}
    ).status_code == 401

    # Invalid offset
    assert client.post(
        url,
        headers=headers,
        json={"offset": -1},
    ).status_code == 422

    # Empty queue
    empty = client.post(
        url,
        headers=headers,
        json={"timeout": 0},
    )
    assert empty.status_code == 200
    assert empty.json() == {
        "ok": True,
        "result": [],
    }

    # Insert an expired and a fresh event
    Session, _ = session_factory

    async def add_events():
        async with Session() as db:
            db.add_all([
                BotUpdate(
                    bot_id=bot_id,
                    room_id=room_id,
                    update_type="message",
                    payload=json.dumps({
                        "message": {"text": "old"}
                    }),
                    created_at=(
                        utc_now() - timedelta(days=8)
                    ),
                ),
                BotUpdate(
                    bot_id=bot_id,
                    room_id=room_id,
                    update_type="message",
                    payload=json.dumps({
                        "message": {"text": "hello"}
                    }),
                ),
            ])
            await db.commit()

    asyncio.run(add_events())

    # Old event is removed, fresh event is returned
    received = client.post(
        url,
        headers=headers,
        json={"limit": 10},
    )
    assert received.status_code == 200

    events = received.json()["result"]
    assert len(events) == 1
    assert events[0]["message"]["text"] == "hello"

    update_id = events[0]["update_id"]

    # Without offset advancement, event repeats
    repeated = client.post(
        url,
        headers=headers,
        json={},
    )
    assert (
        repeated.json()["result"][0]["update_id"]
        == update_id
    )

    # Acknowledge processed event
    acked = client.post(
        url,
        headers=headers,
        json={
            "offset": update_id + 1,
            "timeout": 1,
        },
    )
    assert acked.status_code == 200
    assert acked.json()["result"] == []

    # Disabling the bot rejects further polling
    disabled = client.patch(
        f"/api/bots/{bot_id}/status",
        headers=owner,
        json={"is_active": False},
    )
    assert disabled.status_code == 200

    assert client.post(
        url,
        headers=headers,
        json={},
    ).status_code == 401
