import pytest
from fastapi import HTTPException

import services.uploads as uploads_module
from services.uploads import (
    build_attachment_path,
    detect_mime_by_magic,
    sanitize_filename,
    validate_upload_file_type,
)
from tests.helpers import create_room_and_join, register


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


@pytest.mark.parametrize(
    "content, expected",
    [
        (b"\xff\xd8\xff\xe0" + b"x" * 20, "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n" + b"x" * 20, "image/png"),
        (b"GIF89a" + b"x" * 20, "image/gif"),
        (b"RIFFxxxxWEBP" + b"x" * 20, "image/webp"),
        (b"%PDF-1.7\n" + b"x" * 20, "application/pdf"),
        (b"PK\x03\x04" + b"x" * 20, "application/zip"),
        (b"7z\xbc\xaf\x27\x1c" + b"x" * 20, "application/x-7z-compressed"),
        (b"Rar!\x1a\x07\x00" + b"x" * 20, "application/vnd.rar"),
        (b"hello world", "text/plain"),
    ],
)
def test_detect_mime_by_magic(content, expected):
    assert detect_mime_by_magic(content) == expected


@pytest.mark.parametrize(
    "filename, declared_mime, content, expected_mime, expected_content_type",
    [
        (
            "photo.jpg",
            "image/jpeg",
            b"\xff\xd8\xff\xe0" + b"x" * 20,
            "image/jpeg",
            "image",
        ),
        (
            "image.png",
            "image/png",
            b"\x89PNG\r\n\x1a\n" + b"x" * 20,
            "image/png",
            "image",
        ),
        (
            "anim.gif",
            "image/gif",
            b"GIF89a" + b"x" * 20,
            "image/gif",
            "image",
        ),
        (
            "doc.pdf",
            "application/pdf",
            b"%PDF-1.7\n" + b"x" * 20,
            "application/pdf",
            "file",
        ),
        (
            "text.txt",
            "text/plain",
            b"hello world",
            "text/plain",
            "file",
        ),
        (
            "archive.zip",
            "application/zip",
            b"PK\x03\x04" + b"x" * 20,
            "application/zip",
            "file",
        ),
        (
            "document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"PK\x03\x04" + b"x" * 20,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "file",
        ),
    ],
)
def test_validate_upload_file_type_accepts(
    filename,
    declared_mime,
    content,
    expected_mime,
    expected_content_type,
):
    mime_type, content_type = validate_upload_file_type(
        filename,
        declared_mime,
        content,
    )

    assert mime_type == expected_mime
    assert content_type == expected_content_type


@pytest.mark.parametrize(
    "filename, declared_mime, content, expected_detail",
    [
        (
            "script.exe",
            "application/x-msdownload",
            b"MZ" + b"x" * 20,
            "File extension is not allowed",
        ),
        (
            "page.html",
            "text/html",
            b"<html></html>",
            "File extension is not allowed",
        ),
        (
            "code.js",
            "application/javascript",
            b"alert(1)",
            "File extension is not allowed",
        ),
        (
            "image.svg",
            "image/svg+xml",
            b"<svg></svg>",
            "File extension is not allowed",
        ),
        (
            "unknown.xyz",
            "application/x-unknown",
            b"\x00\x01\x02\x03",
            "File type is not allowed",
        ),
        (
            "fake.jpg",
            "image/jpeg",
            b"%PDF-1.7\n" + b"x" * 20,
            "File type is not allowed",
        ),
    ],
)
def test_validate_upload_file_type_rejects(
    filename,
    declared_mime,
    content,
    expected_detail,
):
    with pytest.raises(HTTPException) as exc:
        validate_upload_file_type(filename, declared_mime, content)

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