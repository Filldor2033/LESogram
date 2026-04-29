from fastapi import APIRouter, WebSocket
from sqlalchemy import select
from urllib.parse import urlparse
from fastapi import WebSocketDisconnect

from database import SessionLocal
from models import User, Room
from core.config import MAX_MESSAGE_LENGTH
from core.rate_limit import (
    get_client_ip_from_websocket,
    enforce_websocket_rate_limit,
)
from services.rooms import (
    verify_room_token,
    room_members,
    build_system_payload,
)
from services.messages import save_message, serialize_message
from ws.manager import manager
from utils.time import utc_now

router = APIRouter()


def websocket_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host")

    if not origin or not host:
        return True

    parsed = urlparse(origin)
    return parsed.netloc.lower() == host.lower()


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    if not websocket_origin_allowed(websocket):
        await websocket.close(code=1008)
        return

    client_ip = get_client_ip_from_websocket(websocket)
    if not enforce_websocket_rate_limit(websocket, "ws_connect", client_ip, 25, 60):
        await websocket.close(code=1013)
        return

    token = websocket.query_params.get("room_token")
    username = verify_room_token(token, room)

    if not username:
        await websocket.close(code=1008)
        return

    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close(code=1008)
            return

        result = await db.execute(select(Room).where(Room.name == room))

        existing_room = result.scalar_one_or_none()

    if not existing_room:
        await websocket.close(code=1008)
        return

    is_admin = bool(user.is_admin)

    await manager.connect(websocket, room)

    was_offline = room_members[room][username] == 0
    room_members[room][username] += 1

    if was_offline:
        await manager.broadcast_json(
            build_system_payload(room, username, "joined"), room
        )

    try:
        while True:
            data = await websocket.receive_json()

            event_type = data.get("type")

            if event_type == "typing":
                await manager.broadcast_json(
                    {
                        "type": "typing",
                        "room": room,
                        "username": username,
                        "is_typing": bool(data.get("is_typing")),
                        "timestamp": utc_now().isoformat(),
                    },
                    room,
                    exclude=websocket,
                )
                continue

            text = (data.get("text") or "").strip()
            reply_to_id = data.get("reply_to_id")

            if reply_to_id is not None:
                try:
                    reply_to_id = int(reply_to_id)
                except (TypeError, ValueError):
                    reply_to_id = None

            if not text or len(text) > MAX_MESSAGE_LENGTH:
                continue

            message_bucket = f"{room}:{username}:{client_ip}"
            if not is_admin and not enforce_websocket_rate_limit(
                websocket, "ws_message", message_bucket, 25, 10
            ):
                await websocket.send_json(
                    {
                        "type": "system",
                        "text": "Rate limit exceeded",
                        "room": room,
                        "timestamp": utc_now().isoformat(),
                        "system_event": "rate_limited",
                        "system_actor": username,
                    }
                )
                continue

            async with SessionLocal() as db:
                message = await save_message(
                    db,
                    username=username,
                    room=room,
                    text=text,
                    content_type="text",
                    reply_to_id=reply_to_id,
                )

            await manager.broadcast_json(serialize_message(message), room)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print("WebSocket error:", repr(exc))
    finally:
        manager.disconnect(websocket, room)

        went_offline = False

        if room in room_members and username in room_members[room]:
            room_members[room][username] -= 1

            if room_members[room][username] <= 0:
                del room_members[room][username]
                went_offline = True

            if not room_members[room]:
                del room_members[room]

        if went_offline:
            await manager.broadcast_json(
                build_system_payload(room, username, "left"), room
            )
