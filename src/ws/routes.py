import asyncio
import contextlib
from urllib.parse import urlparse

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from core.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT, MAX_MESSAGE_LENGTH
from core.rate_limit import check_duplicate_message_limit, check_websocket_rate_limit, enforce_websocket_rate_limit, get_client_ip_from_websocket
from database import SessionLocal
from models import Room, User
from services.messages import save_message, serialize_message
from services.parse import extract_mentions
from services.rooms import build_system_payload, room_members, verify_room_token
from utils.time import utc_now
from ws.events import handle_message_event, handle_typing_event
from ws.heartbeat import heartbeat
from ws.manager import manager

router = APIRouter()


def websocket_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host")

    if not origin or not host:
        return True

    parsed = urlparse(origin)
    return parsed.netloc.lower() == host.lower()


async def authenticate_websocket(websocket: WebSocket, room: str):
    token = websocket.query_params.get("room_token")
    username = verify_room_token(token, room)

    if not username:
        return None, None

    async with SessionLocal() as db:
        user_result = await db.execute(
            select(User).where(User.username == username)
        )
        user = user_result.scalar_one_or_none()

        room_result = await db.execute(
            select(Room).where(Room.name == room)
        )
        existing_room = room_result.scalar_one_or_none()

    if not user or not existing_room:
        return None, None

    return username, user


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    if not websocket_origin_allowed(websocket):
        await websocket.close(code=1008)
        return

    client_ip = get_client_ip_from_websocket(websocket)
    connect_retry_after = await check_websocket_rate_limit(
        "ws_connect",
        client_ip,
        25,
        60,
    )

    if connect_retry_after is not None:
        await websocket.close(code=1013)
        return

    username, user = await authenticate_websocket(websocket, room)

    is_admin = bool(user.is_admin)

    await manager.connect(websocket, room)
    websocket.state.username = username
    websocket.state.last_seen = utc_now()
    
    heartbeat_task = asyncio.create_task(
        heartbeat(websocket, manager._send_safe)
    )

    was_offline = room_members[room][username] == 0
    room_members[room][username] += 1

    if was_offline:
        await manager.broadcast_json(
            build_system_payload(room, username, "joined"), room
        )

    try:
        while True:
            data = await websocket.receive_json()
            websocket.state.last_seen = utc_now()

            event_type = data.get("type")

            if event_type == "pong":
                continue

            if event_type == "typing":
                await handle_typing_event(
                    data=data,
                    websocket=websocket,
                    room=room,
                    username=username,
                    client_ip=client_ip,
                    is_admin=is_admin,
                )
                continue

            await handle_message_event(
                data=data,
                websocket=websocket,
                db_factory=SessionLocal,
                room=room,
                username=username,
                client_ip=client_ip,
                is_admin=is_admin,
            )

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print("WebSocket error:", repr(exc))
    finally:
        heartbeat_task.cancel()
        
        with contextlib.suppress(asyncio.CancelledError):
            await heartbeat_task
        
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
