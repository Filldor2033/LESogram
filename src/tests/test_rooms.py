from jose import jwt

from auth import ALGORITHM, SECRET_KEY
from schemas import CreateRoomRequest, JoinRoomRequest
from services.rooms import build_system_payload, verify_room_token


def test_verify_room_token_invalid_cases():
    assert verify_room_token(None, "room1") is None
    assert verify_room_token("invalid.token.here", "room1") is None

    token = jwt.encode(
        {"sub": "test1", "type": "wrong_type", "room": "room1"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert verify_room_token(token, "room1") is None

    token = jwt.encode(
        {"sub": "test1", "type": "room_access", "room": "other_room"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert verify_room_token(token, "room1") is None

    token = jwt.encode(
        {"sub": "test1", "type": "room_access", "room": "room1"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert verify_room_token(token, "room1") == "test1"


def test_verify_room_token_jwt_error():
    assert verify_room_token("not.even.valid.jwt", "room1") is None
    assert verify_room_token("", "room1") is None


def test_build_system_payload():
    payload = build_system_payload("general", "test1", "joined")

    assert payload["type"] == "system"
    assert "test1 joined" in payload["text"]
    assert payload["system_event"] == "joined"
    assert payload["system_actor"] == "test1"
    assert "timestamp" in payload


def test_create_room_request_short_name():
    try:
        CreateRoomRequest(name="ab", password="pass")
    except ValueError as exc:
        assert "at least 3 characters" in str(exc)
    else:
        assert False


def test_create_room_request_newlines():
    try:
        CreateRoomRequest(name="room\nname", password="pass")
    except ValueError as exc:
        assert "cannot contain newlines" in str(exc)
    else:
        assert False


def test_join_room_request_empty_room():
    try:
        JoinRoomRequest(room="   ", password="pass")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        assert False


def test_join_room_request_invalid_room_chars():
    try:
        JoinRoomRequest(room="room<script>", password="pass")
    except ValueError:
        pass
    else:
        assert False
