import asyncio
from sqlalchemy import select

from models import User


def register(client, username="alice", password="secret123"):
    response = client.post(
        "/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_room_and_join(client, headers, room="general", password="roompass"):
    response = client.post(
        "/rooms",
        headers=headers,
        json={"name": room, "password": password},
    )
    assert response.status_code == 200, response.text

    response = client.post(
        "/rooms/join",
        headers=headers,
        json={"room": room, "password": password},
    )
    assert response.status_code == 200, response.text

    return response.json()["room_token"]


def make_admin(session_factory, username: str):
    TestingSessionLocal, _ = session_factory

    async def _make_admin():
        async with TestingSessionLocal() as db:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            assert user is not None

            user.is_admin = True
            await db.commit()

    asyncio.run(_make_admin())
