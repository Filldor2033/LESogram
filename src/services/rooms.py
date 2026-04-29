from jose import JWTError, jwt
from fastapi import HTTPException
from sqlalchemy import select

from auth import ALGORITHM, SECRET_KEY
from models import Room
from utils.time import utc_now
from collections import Counter, defaultdict

room_members: dict[str, Counter[str]] = defaultdict(Counter)


def verify_room_token(token: str | None, room: str) -> str | None:
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "room_access":
            return None

        if payload.get("room") != room:
            return None

        return payload.get("sub")

    except JWTError:
        return None


async def require_room_access(room: str, room_token: str, db):
    username = verify_room_token(room_token, room)

    if not username:
        raise HTTPException(status_code=403, detail="No access to this room")

    result = await db.execute(select(Room).where(Room.name == room))

    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Room not found")

    return username


def build_system_payload(room: str, actor: str, event: str) -> dict:
    return {
        "type": "system",
        "text": f"{actor} {event}",
        "room": room,
        "timestamp": utc_now().isoformat(),
        "system_event": event,
        "system_actor": actor,
    }
