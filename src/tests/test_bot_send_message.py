from tests.helpers import register


def test_bot_send_message(client):
    # Create regular user
    owner = register(client, "alice")

    # Create room
    room_response = client.post(
        "/api/rooms",
        headers=owner,
        json={
            "name": "general",
            "password": "roompass",
        },
    )
    assert room_response.status_code == 200
    room_id = room_response.json()["room_id"]

    # Create bot
    created = client.post(
        "/api/bots",
        headers=owner,
        json={
            "username": "echo_bot",
            "display_name": "Echo Bot",
        },
    )
    assert created.status_code == 201

    bot = created.json()
    bot_id = bot["id"]

    headers = {
        "Authorization": f"Bot {bot['token']}"
    }

    send_url = "/api/bot/sendMessage"
    payload = {
        "chat_id": room_id,
        "text": "Hello from bot!",
    }

    # No room permission yet
    denied = client.post(
        send_url,
        headers=headers,
        json=payload,
    )
    assert denied.status_code == 403

    # Grant sending permission
    added = client.post(
        f"/api/rooms/{room_id}/bots",
        headers=owner,
        json={
            "username": "echo_bot",
            "can_read_messages": False,
            "can_send_messages": True,
        },
    )
    assert added.status_code == 201

    # Send message
    sent = client.post(
        send_url,
        headers=headers,
        json=payload,
    )
    assert sent.status_code == 200, sent.text

    result = sent.json()["result"]

    assert sent.json()["ok"] is True
    assert result["chat_id"] == room_id
    assert result["username"] == "echo_bot"
    assert result["text"] == "Hello from bot!"

    # Reply to the first message
    reply = client.post(
        send_url,
        headers=headers,
        json={
            "chat_id": room_id,
            "text": "This is a reply",
            "reply_to_id": result["message_id"],
        },
    )
    assert reply.status_code == 200
    assert (
        reply.json()["result"]["reply_to_id"]
        == result["message_id"]
    )

    # Revoke sending permission
    changed = client.patch(
        f"/api/rooms/{room_id}/bots/{bot_id}",
        headers=owner,
        json={"can_send_messages": False},
    )
    assert changed.status_code == 200

    denied_again = client.post(
        send_url,
        headers=headers,
        json=payload,
    )
    assert denied_again.status_code == 403
