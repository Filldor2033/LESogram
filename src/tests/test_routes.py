from tests.helpers import register, create_room_and_join, make_admin


def test_create_room_requires_auth(client):
    response = client.post(
        "/rooms",
        json={"name": "general", "password": "roompass"},
    )

    assert response.status_code == 401


def test_room_join_wrong_and_correct_password(client):
    alice_headers = register(client, "alice", "secret123")

    response = client.post(
        "/rooms",
        headers=alice_headers,
        json={"name": "general", "password": "roompass"},
    )

    assert response.status_code == 200

    bob_headers = register(client, "bob", "secret123")

    response = client.post(
        "/rooms/join",
        headers=bob_headers,
        json={"room": "general", "password": "wrong"},
    )

    assert response.status_code == 403

    response = client.post(
        "/rooms/join",
        headers=bob_headers,
        json={"room": "general", "password": "roompass"},
    )

    assert response.status_code == 200
    assert "room_token" in response.json()


def test_list_rooms_unauthorized(client):
    response = client.get("/rooms")
    assert response.status_code == 401


def test_message_history_requires_room_token(client):
    headers = register(client)
    room_token = create_room_and_join(client, headers)

    response = client.get("/messages/general?room_token=bad-token")
    assert response.status_code == 403

    response = client.get(f"/messages/general?room_token={room_token}")
    assert response.status_code == 200

    data = response.json()
    assert data["messages"] == []
    assert data["has_more"] is False
    assert data["next_before_id"] is None


def test_get_messages_invalid_token(client):
    headers = register(client)
    create_room_and_join(client, headers)

    response = client.get("/messages/general?room_token=invalid")
    assert response.status_code == 403


def test_websocket_send_message_and_history(client):
    headers = register(client)
    room_token = create_room_and_join(client, headers)

    with client.websocket_connect(f"/ws/general?room_token={room_token}") as websocket:
        joined_payload = websocket.receive_json()

        assert joined_payload["type"] == "system"
        assert joined_payload["system_event"] == "joined"

        websocket.send_json({"text": "Hello world"})

        message_payload = websocket.receive_json()

        assert message_payload["type"] == "message"
        assert message_payload["username"] == "alice"
        assert message_payload["text"] == "Hello world"
        assert message_payload["room"] == "general"

    response = client.get(f"/messages/general?room_token={room_token}")

    assert response.status_code == 200
    messages = response.json()["messages"]

    assert len(messages) == 1
    assert messages[0]["text"] == "Hello world"


def test_only_admin_can_delete_message(client, session_factory):
    alice_headers = register(client, "alice", "secret123")
    room_token = create_room_and_join(client, alice_headers)

    upload_response = client.post(
        "/rooms/general/attachments",
        headers=alice_headers,
        data={"room_token": room_token, "text": "delete me"},
        files={"file": ("note.txt", b"hello", "text/plain")},
    )

    assert upload_response.status_code == 200

    message_id = upload_response.json()["id"]

    response = client.delete(
        f"/messages/{message_id}",
        headers=alice_headers,
    )

    assert response.status_code == 403

    make_admin(session_factory, "alice")

    response = client.delete(
        f"/messages/{message_id}",
        headers=alice_headers,
    )

    assert response.status_code == 200
    assert response.json()["message_id"] == message_id


def test_delete_message_not_found(client, session_factory):
    headers = register(client, "testuser", "pass123")
    make_admin(session_factory, "testuser")

    response = client.delete("/messages/999999", headers=headers)

    assert response.status_code == 404


def test_only_creator_or_admin_can_delete_room(client):
    alice_headers = register(client, "alice", "secret123")
    bob_headers = register(client, "bob", "secret123")

    create_room_and_join(client, alice_headers, room="general")

    response = client.delete("/rooms/general", headers=bob_headers)
    assert response.status_code == 403

    response = client.delete("/rooms/general", headers=alice_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_room_not_found(client):
    headers = register(client)

    response = client.delete("/rooms/nonexistent", headers=headers)

    assert response.status_code == 404
