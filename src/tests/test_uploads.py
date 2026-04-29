import pytest
from fastapi import HTTPException

import services.uploads as uploads_module
from services.uploads import (
    sanitize_filename,
    determine_upload_content_type,
    build_attachment_path,
)

from tests.helpers import register, create_room_and_join


def test_sanitize_filename_edge_cases():
    assert sanitize_filename("file<script>.exe") == "file_script_.exe"
    assert sanitize_filename("   ") == "attachment"
    assert sanitize_filename("a" * 300) == "a" * 255
    assert sanitize_filename(None) == "attachment"


@pytest.mark.parametrize(
    "input_name, expected",
    [
        (None, "attachment"),
        ("", "attachment"),
        ("   ", "attachment"),
        ("a" * 300, "a" * 255),
        ("file<script>.exe", "file_script_.exe"),
        ("../etc/passwd", "passwd"),
        (" normal.txt ", "normal.txt"),
    ],
)
def test_sanitize_filename_parametrized(input_name, expected):
    assert sanitize_filename(input_name) == expected


def test_determine_upload_content_type_blocked_types():
    with pytest.raises(HTTPException) as exc:
        determine_upload_content_type("anim.gif", "image/gif")
    assert "GIF" in exc.value.detail

    with pytest.raises(HTTPException):
        determine_upload_content_type("script.exe", "application/x-msdownload")

    with pytest.raises(HTTPException):
        determine_upload_content_type("page.html", "text/html")

    with pytest.raises(HTTPException):
        determine_upload_content_type("weird.xyz", "application/x-unknown")


@pytest.mark.parametrize(
    "filename, mime_type, expected_detail",
    [
        ("anim.gif", "image/gif", "GIF uploads are disabled"),
        ("script.exe", "application/x-msdownload", "File type is not allowed"),
        ("page.html", "text/html", "File type is not allowed"),
        ("code.js", "application/javascript", "File type is not allowed"),
        ("image.svg", "image/svg+xml", "File type is not allowed"),
        ("unknown.xyz", "application/x-unknown", "File type is not allowed"),
    ],
)
def test_determine_upload_content_type_rejects(filename, mime_type, expected_detail):
    with pytest.raises(HTTPException) as exc:
        determine_upload_content_type(filename, mime_type)

    assert exc.value.status_code == 400
    assert expected_detail in exc.value.detail


def test_build_attachment_path_security():
    path = build_attachment_path("/uploads/file.txt")

    assert path is not None
    assert path.name == "file.txt"

    path = build_attachment_path("/uploads/../../../etc/passwd")

    assert path is not None
    assert path.name == "passwd"

    resolved_uploads = uploads_module.UPLOADS_DIR.resolve()
    resolved_path = path.resolve()

    assert (
        resolved_uploads in resolved_path.parents
        or resolved_path.parent == resolved_uploads
    )

    assert build_attachment_path("/other/file.txt") is None
    assert build_attachment_path(None) is None
    assert build_attachment_path("") is None


@pytest.mark.parametrize(
    "media_url, expected_name, should_exist",
    [
        ("/uploads/doc.pdf", "doc.pdf", True),
        ("/uploads/../../../etc/passwd", "passwd", True),
        ("/uploads/subdir/image.png", "image.png", True),
        ("/other/file.txt", None, False),
        ("", None, False),
        (None, None, False),
    ],
)
def test_build_attachment_path_variants(media_url, expected_name, should_exist):
    path = build_attachment_path(media_url)

    if should_exist:
        assert path is not None
        assert path.name == expected_name

        resolved_uploads = uploads_module.UPLOADS_DIR.resolve()
        resolved_path = path.resolve()

        assert (
            resolved_uploads in resolved_path.parents
            or resolved_path.parent == resolved_uploads
        )
    else:
        assert path is None


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
    import api.attachment_routes as attachment_routes

    monkeypatch.setattr(attachment_routes, "MAX_UPLOAD_SIZE", 10)

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
    msg_id = resp.json()["messages"][-1]["id"]

    response = client.get(f"/attachments/{msg_id}?room_token=" + room_token)

    assert response.status_code == 404
