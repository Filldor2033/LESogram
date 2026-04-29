import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from auth import SECRET_KEY, ALGORITHM
import main
from schemas import RegisterRequest, LoginRequest, CreateRoomRequest, JoinRoomRequest

def test_get_client_ip_from_request_with_none_client():
    request = Mock()
    request.client = None
    ip = main.get_client_ip_from_request(request)
    assert ip == "unknown"


def test_get_client_ip_from_websocket_with_none_client():
    websocket = Mock()
    websocket.client = None
    ip = main.get_client_ip_from_websocket(websocket)
    assert ip == "unknown"


def test_normalize_message_text_too_long():
    long_text = "x" * (main.MAX_MESSAGE_LENGTH + 1)
    with pytest.raises(HTTPException) as exc:
        main.normalize_message_text(long_text, allow_empty=False)
    assert exc.value.status_code == 400
    assert "at most" in exc.value.detail


def test_normalize_message_text_empty_not_allowed():
    with pytest.raises(HTTPException) as exc:
        main.normalize_message_text("   ", allow_empty=False)
    assert exc.value.status_code == 400
    assert "cannot be empty" in exc.value.detail


def test_normalize_message_text_empty_allowed():
    result = main.normalize_message_text("  \n  ", allow_empty=True)
    assert result == ""


def test_sanitize_filename_edge_cases():
    assert main.sanitize_filename("file<script>.exe") == "file_script_.exe"
    assert main.sanitize_filename("   ") == "attachment"
    assert main.sanitize_filename("a" * 300) == "a" * 255
    assert main.sanitize_filename(None) == "attachment"


def test_determine_upload_content_type_blocked_types():
    with pytest.raises(HTTPException) as exc:
        main.determine_upload_content_type("anim.gif", "image/gif")
    assert "GIF" in exc.value.detail

    with pytest.raises(HTTPException):
        main.determine_upload_content_type("script.exe", "application/x-msdownload")

    with pytest.raises(HTTPException):
        main.determine_upload_content_type("page.html", "text/html")

    with pytest.raises(HTTPException):
        main.determine_upload_content_type("weird.xyz", "application/x-unknown")


def test_build_attachment_path_security():
    path = main.build_attachment_path("/uploads/file.txt")
    assert path is not None
    assert path.name == "file.txt"
    
    path = main.build_attachment_path("/uploads/../../../etc/passwd")
    assert path is not None
    assert path.name == "passwd"
    assert main.UPLOADS_DIR.resolve() in path.resolve().parents or path.resolve() == main.UPLOADS_DIR.resolve() / "passwd"
    
    path = main.build_attachment_path("/other/file.txt")
    assert path is None
    
    assert main.build_attachment_path(None) is None
    assert main.build_attachment_path("") is None


def test_verify_room_token_invalid_cases():
    assert main.verify_room_token(None, "room1") is None

    assert main.verify_room_token("invalid.token.here", "room1") is None

    token = jwt.encode({"sub": "test1", "type": "wrong_type", "room": "room1"}, SECRET_KEY, algorithm=ALGORITHM)
    assert main.verify_room_token(token, "room1") is None

    token = jwt.encode({"sub": "test1", "type": "room_access", "room": "other_room"}, SECRET_KEY, algorithm=ALGORITHM)
    assert main.verify_room_token(token, "room1") is None

    token = jwt.encode({"sub": "test1", "type": "room_access", "room": "room1"}, SECRET_KEY, algorithm=ALGORITHM)
    assert main.verify_room_token(token, "room1") == "test1"


def test_build_system_payload():
    payload = main.build_system_payload("general", "test1", "joined")
    assert payload["type"] == "system"
    assert "test1 joined" in payload["text"]
    assert payload["system_event"] == "joined"
    assert payload["system_actor"] == "test1"
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_connection_manager_broadcast_with_dead_connections():
    manager = main.ConnectionManager()
    
    ws_good = Mock()
    ws_good.send_json = AsyncMock()
    
    ws_dead = Mock()
    ws_dead.send_json = AsyncMock(side_effect=ConnectionError("dead"))
    
    room = "test_room"
    manager.active_connections[room] = [ws_good, ws_dead]
    
    await manager.broadcast_json({"type": "test"}, room)
    
    ws_good.send_json.assert_called_once()

    assert ws_dead not in manager.active_connections.get(room, [])


@pytest.mark.asyncio
async def test_connection_manager_close_room():
    manager = main.ConnectionManager()
    
    ws = Mock()
    ws.close = AsyncMock()
    manager.active_connections["temp_room"] = [ws]
    
    await manager.close_room("temp_room", code=1001)
    
    ws.close.assert_called_once_with(code=1001)
    assert "temp_room" not in manager.active_connections


def test_register_request_invalid_username_chars():
    with pytest.raises(ValueError) as exc:
        RegisterRequest(username="escapetest<script>", password="secret123")
    assert "invalid characters" in str(exc.value)


def test_login_request_invalid_username_chars():
    with pytest.raises(ValueError):
        LoginRequest(username="bob\nadmin", password="secret")


def test_create_room_request_short_name():
    with pytest.raises(ValueError) as exc:
        CreateRoomRequest(name="ab", password="pass")
    assert "at least 3 characters" in str(exc.value)


def test_create_room_request_newlines():
    with pytest.raises(ValueError) as exc:
        CreateRoomRequest(name="room\nname", password="pass")
    assert "cannot contain newlines" in str(exc.value)


def test_join_room_request_empty_room():
    with pytest.raises(ValueError) as exc:
        JoinRoomRequest(room="   ", password="pass")
    assert "cannot be empty" in str(exc.value)


def test_join_room_request_invalid_room_chars():
    with pytest.raises(ValueError):
        JoinRoomRequest(room="room<script>", password="pass")


def test_security_middleware_https_headers(client):
    from starlette.datastructures import URL
    
    from starlette.requests import Request
    from starlette.responses import Response
    
    async def dummy_call_next(request):
        return Response(content="ok")
    
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "scheme": "https",
        "server": ("testserver", 443),
        "headers": [],
    }
    request = Request(scope)
    
    import asyncio
    response = asyncio.run(main.add_security_headers(request, dummy_call_next))
    
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    
    scope["scheme"] = "http"
    request = Request(scope)
    response = asyncio.run(main.add_security_headers(request, dummy_call_next))
    assert "Strict-Transport-Security" not in response.headers


def test_security_middleware_cache_control(client):
    response = client.get("/login")
    assert response.headers.get("Cache-Control") == "no-store"
    
    response = client.get("/register")
    assert response.headers.get("Cache-Control") == "no-store"


def test_get_me_endpoint(client):
    headers = register(client, "testuser", "pass123")
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["is_admin"] is False


def test_list_rooms_unauthorized(client):
    response = client.get("/rooms")
    assert response.status_code == 401


def test_get_messages_invalid_token(client):
    headers = register(client)
    create_room_and_join(client, headers)
    
    response = client.get("/messages/general?room_token=invalid")
    assert response.status_code == 403


def test_get_attachment_not_found(client):
    headers = register(client)
    room_token = create_room_and_join(client, headers)
    
    response = client.get("/attachments/999999?room_token=" + room_token)
    assert response.status_code == 404


def test_upload_attachment_empty_file(client):
    headers = register(client)
    room_token = create_room_and_join(client, headers)
    
    response = client.post(
        "/rooms/general/attachments",
        headers=headers,
        data={"room_token": room_token},
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_upload_attachment_too_large(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_UPLOAD_SIZE", 10)
    
    headers = register(client)
    room_token = create_room_and_join(client, headers)
    
    response = client.post(
        "/rooms/general/attachments",
        headers=headers,
        data={"room_token": room_token},
        files={"file": ("big.txt", b"x" * 100, "text/plain")},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_delete_message_not_found(client, session_factory):
    headers = register(client)
    make_admin(session_factory, "testuser")
    
    response = client.delete("/messages/999999", headers=headers)
    assert response.status_code == 404


def test_delete_room_not_found(client):
    headers = register(client)
    response = client.delete("/rooms/nonexistent", headers=headers)
    assert response.status_code == 404


def test_enforce_http_rate_limit_triggers(client, monkeypatch):
    mock_hit = Mock(return_value=30)
    monkeypatch.setattr(main.rate_limiter, "hit", mock_hit)
    
    from fastapi import HTTPException
    
    request = Mock()
    request.client = Mock(host="127.0.0.1")
    
    with pytest.raises(HTTPException) as exc:
        main.enforce_http_rate_limit(request, "test_bucket", limit=1, window_seconds=60)
    
    assert exc.value.status_code == 429
    assert "Retry in 30 seconds" in exc.value.detail
    mock_hit.assert_called_once()


def test_verify_room_token_jwt_error():
    result = main.verify_room_token("not.even.valid.jwt", "room1")
    assert result is None
    
    assert main.verify_room_token("", "room1") is None


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_dead():
    manager = main.ConnectionManager()
    
    ws_alive = Mock()
    ws_alive.send_json = AsyncMock()
    
    ws_dead = Mock()
    ws_dead.send_json = AsyncMock(side_effect=RuntimeError("Connection lost"))
    
    room = "test"
    manager.active_connections[room] = [ws_alive, ws_dead]
    
    await manager.broadcast_json({"type": "ping"}, room)
    
    ws_alive.send_json.assert_called_once_with({"type": "ping"})

    assert ws_dead not in manager.active_connections.get(room, [])
    assert ws_alive in manager.active_connections.get(room, [])


def test_get_attachment_cascade_404(client):
    headers = register(client)
    room_token = create_room_and_join(client, headers)
    
    response = client.get("/attachments/999999?room_token=" + room_token)
    assert response.status_code == 404
    assert "Attachment not found" in response.json()["detail"]
    
    with client.websocket_connect(f"/ws/general?room_token={room_token}") as ws:
        ws.receive_json()
        ws.send_json({"text": "no file"})
        ws.receive_json()
    
    resp = client.get(f"/messages/general?room_token={room_token}")
    msg_id = resp.json()[-1]["id"]
    
    response = client.get(f"/attachments/{msg_id}?room_token=" + room_token)
    assert response.status_code == 404


@pytest.mark.parametrize("input_name, expected", [
    (None, "attachment"),
    ("", "attachment"),
    ("   ", "attachment"),
    ("a" * 300, "a" * 255),
    ("file<script>.exe", "file_script_.exe"),
    ("../etc/passwd", "passwd"),
    (" normal.txt ", "normal.txt"),
])
def test_sanitize_filename_parametrized(input_name, expected):
    assert main.sanitize_filename(input_name) == expected


@pytest.mark.parametrize("media_url, expected_name, should_exist", [
    ("/uploads/doc.pdf", "doc.pdf", True),
    ("/uploads/../../../etc/passwd", "passwd", True),
    ("/uploads/subdir/image.png", "image.png", True),
    ("/other/file.txt", None, False),
    ("", None, False),
    (None, None, False),
])
def test_build_attachment_path_variants(media_url, expected_name, should_exist):
    path = main.build_attachment_path(media_url)
    if should_exist:
        assert path is not None
        assert path.name == expected_name
        resolved_uploads = main.UPLOADS_DIR.resolve()
        resolved_path = path.resolve()
        assert resolved_uploads in resolved_path.parents or resolved_path.parent == resolved_uploads
    else:
        assert path is None


@pytest.mark.parametrize("filename, mime_type, expected_detail", [
    ("anim.gif", "image/gif", "GIF uploads are disabled"),
    ("script.exe", "application/x-msdownload", "File type is not allowed"),
    ("page.html", "text/html", "File type is not allowed"),
    ("code.js", "application/javascript", "File type is not allowed"),
    ("image.svg", "image/svg+xml", "File type is not allowed"),
    ("unknown.xyz", "application/x-unknown", "File type is not allowed"),
])
def test_determine_upload_content_type_rejects(filename, mime_type, expected_detail):
    with pytest.raises(HTTPException) as exc:
        main.determine_upload_content_type(filename, mime_type)
    assert exc.value.status_code == 400
    assert expected_detail in exc.value.detail


def register(client, username="testuser", password="pass123"):
    response = client.post("/register", json={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_room_and_join(client, headers, room="general", password="roompass"):
    client.post("/rooms", headers=headers, json={"name": room, "password": password})
    response = client.post("/rooms/join", headers=headers, json={"room": room, "password": password})
    assert response.status_code == 200
    return response.json()["room_token"]


def make_admin(session_factory, username="testuser"):
    TestingSessionLocal, _ = session_factory
    db = TestingSessionLocal()
    try:
        from models import User
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_admin = True
            db.commit()
    finally:
        db.close()

try:
    from unittest.mock import AsyncMock
except ImportError:
    # Python < 3.8
    from asynctest import CoroutineMock as AsyncMock