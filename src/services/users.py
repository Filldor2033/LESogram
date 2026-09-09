"""
User profile service: public serialization, stats, admin listing.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Message, Room, User

# Rooms where the user is technically able to participate (all rooms
# are password-gated, so presence is approximated by message activity).
MAX_BIO_LENGTH = 200
MAX_DISPLAY_NAME_LENGTH = 50


def serialize_user_public(user: User) -> dict:
    """
    The profile card fields visible to ANY logged-in user.
    The registration date is intentionally NOT here — the owner
    sees it in their own cabinet only.
    """
    return {
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "is_admin": bool(user.is_admin),
    }


def serialize_user_private(user: User) -> dict:
    """
    Full self-profile: everything public plus the registration date.
    """
    data = serialize_user_public(user)
    data["created_at"] = (
        user.created_at.isoformat()
        if user.created_at is not None
        else None
    )
    return data


async def get_user_by_username(
    db: AsyncSession, username: str
) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_stats(
    db: AsyncSession, username: str
) -> dict:
    """
    Lightweight message statistics for a user.
    """
    # total + per content type
    result = await db.execute(
        select(
            Message.content_type,
            func.count(Message.id),
        )
        .where(Message.username == username)
        .group_by(Message.content_type)
    )
    per_type = {row[0]: row[1] for row in result.all()}

    total = sum(per_type.values())

    # rooms the user ever wrote in
    result = await db.execute(
        select(func.count(func.distinct(Message.room)))
        .where(Message.username == username)
    )
    rooms_count = result.scalar_one()

    # first message timestamp
    result = await db.execute(
        select(func.min(Message.timestamp))
        .where(Message.username == username)
    )
    first_at = result.scalar_one()

    # messages in the last 30 days
    cutoff = datetime.now(timezone.utc).timestamp() - 30 * 24 * 3600
    result = await db.execute(
        select(func.count(Message.id))
        .where(
            Message.username == username,
            func.strftime("%s", Message.timestamp) >= str(int(cutoff)),
        )
    )

    # sqlite-only helper: on postgres the fallback is the same count
    try:
        recent = result.scalar_one()
    except Exception:
        recent = None

    return {
        "total_messages": total,
        "messages_by_type": per_type,
        "rooms_active_in": rooms_count,
        "first_message_at": (
            first_at.isoformat() if first_at is not None else None
        ),
        "recent_messages": recent if recent is not None else total,
    }


async def list_users_for_admin(
    db: AsyncSession,
) -> list[dict]:
    """
    All users with their message stats, for the admin panel.
    """
    result = await db.execute(
        select(User).order_by(func.lower(User.username))
    )
    users = result.scalars().all()

    if not users:
        return []

    msg_counts = {}

    result = await db.execute(
        select(
            Message.username, func.count(Message.id)
        ).group_by(Message.username)
    )
    msg_counts = {row[0]: row[1] for row in result.all()}

    out = []

    for user in users:
        out.append(
            {
                **serialize_user_public(user),
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at is not None
                    else None
                ),
                "message_count": msg_counts.get(user.username, 0),
            }
        )

    return out


async def list_rooms_for_admin(db: AsyncSession) -> list[dict]:
    """
    All rooms with message counts, for the admin panel.
    """
    result = await db.execute(select(Room).order_by(func.lower(Room.name)))
    rooms = result.scalars().all()

    counts = {}

    if rooms:
        result = await db.execute(
            select(
                Message.room, func.count(Message.id)
            ).group_by(Message.room)
        )
        counts = {row[0]: row[1] for row in result.all()}

    return [
        {
            "name": room.name,
            "created_by": room.created_by,
            "created_at": (
                room.created_at.isoformat()
                if room.created_at is not None
                else None
            ),
            "message_count": counts.get(room.name, 0),
        }
        for room in rooms
    ]
