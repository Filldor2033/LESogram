from models import Room, User


def can_delete_room(user: User, room: Room) -> bool:
    return room.created_by == user.username or user.is_admin


def can_delete_message(user: User) -> bool:
    return bool(user.is_admin)


def can_skip_room_password(user: User) -> bool:
    return bool(user.is_admin)


def can_skip_rate_limit(user: User) -> bool:
    return bool(user.is_admin)