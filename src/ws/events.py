import asyncio

from sqlalchemy import select

from core.config import MAX_MESSAGE_LENGTH
from core.rate_limit import check_websocket_rate_limit
from models import Message
from services.messages import save_message, serialize_message
from services.parse import extract_mentions
from services.rooms import room_members
from utils.time import utc_now
from ws.manager import manager


async def handle_typing_event(
    *,
    data: dict,
    websocket,
    room: str,
    username: str,
    client_ip: str,
    is_admin: bool,
):
    retry_after = await check_websocket_rate_limit(
        "ws_typing",
        f"{room}:{username}:{client_ip}",
        20,
        10,
    )

    if not is_admin and retry_after is not None:
        return

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


async def handle_message_event(
    *,
    data: dict,
    websocket,
    db_factory,
    room: str,
    username: str,
    client_ip: str,
    is_admin: bool,
):
    text = (data.get("text") or "").strip()

    if not text or len(text) > MAX_MESSAGE_LENGTH:
        return

    bucket = f"{room}:{username}:{client_ip}"

    burst_retry_after = await check_websocket_rate_limit(
        "ws_message_burst",
        bucket,
        5,
        3,
    )

    if not is_admin and burst_retry_after is not None:
        manager._send_safe(
            websocket,
            {
                "type": "system",
                "text": "Too many messages too quickly",
                "room": room,
                "timestamp": utc_now().isoformat(),
                "system_event": "rate_limited",
                "system_actor": username,
                "retry_after": burst_retry_after,
            },
        )
        return

    message_retry_after = await check_websocket_rate_limit(
        "ws_message",
        bucket,
        25,
        10,
    )

    if not is_admin and message_retry_after is not None:
        manager._send_safe(
            websocket,
            {
                "type": "system",
                "text": "Rate limit exceeded",
                "room": room,
                "timestamp": utc_now().isoformat(),
                "system_event": "rate_limited",
                "system_actor": username,
                "retry_after": message_retry_after,
            },
        )
        return

    reply_to_id = data.get("reply_to_id")

    async with db_factory() as db:
        if reply_to_id is not None:
            try:
                reply_to_id = int(reply_to_id)

                reply_result = await db.execute(
                    select(Message).where(
                        Message.id == reply_to_id,
                        Message.room == room,
                    )
                )

                if not reply_result.scalar_one_or_none():
                    reply_to_id = None

            except (TypeError, ValueError):
                reply_to_id = None

        message = await save_message(
            db,
            username=username,
            room=room,
            text=text,
            content_type="text",
            reply_to_id=reply_to_id,
        )

    payload = serialize_message(message)

    await manager.broadcast_json(payload, room)

    mentions = extract_mentions(text)

    room_snapshot = set(room_members.get(room, {}))

    valid_mentions = {
        mentioned_user
        for mentioned_user in mentions
        if (mentioned_user != username and mentioned_user in room_snapshot)
    }

    await asyncio.gather(
        *(
            manager.send_personal_json(
                {
                    "type": "mention",
                    "from": username,
                    "room": room,
                    "text": text,
                    "message": payload,
                    "timestamp": utc_now().isoformat(),
                },
                room,
                mentioned_user,
            )
            for mentioned_user in valid_mentions
        ),
        return_exceptions=True,
    )
