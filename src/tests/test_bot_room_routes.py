from tests.helpers import make_admin, register


def test_bot_room_management(client, session_factory):
    alice = register(client, "alice")
    bob = register(client, "bob")

    room_response = client.post(
        "/api/rooms",
        headers=alice,
        json={
            "name": "general",
            "password": "roompass",
        },
    )
    assert room_response.status_code == 200
    room_id = room_response.json()["room_id"]

    bot_response = client.post(
        "/api/bots",
        headers=alice,
        json={
            "username": "echo_bot",
            "display_name": "Echo Bot",
        },
    )
    assert bot_response.status_code == 201, bot_response.text
    bot_id = bot_response.json()["id"]

    url = f"/api/rooms/{room_id}/bots"

    payload = {
        "username": "echo_bot",
        "can_read_messages": True,
        "can_send_messages": False,
    }

    # Authentication required
    assert client.post(url, json=payload).status_code == 401

    # A regular user cannot add bots
    assert client.post(
        url, headers=bob, json=payload
    ).status_code == 403

    # The room creator can add a bot
    added = client.post(
        url, headers=alice, json=payload
    )
    assert added.status_code == 201, added.text
    assert added.json()["bot_id"] == bot_id

    # Duplicates are rejected
    assert client.post(
        url, headers=alice, json=payload
    ).status_code == 409

    # Only authorized managers can list bots
    assert client.get(url, headers=bob).status_code == 403

    listed = client.get(url, headers=alice)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["can_read_messages"] is True

    bot_url = f"{url}/{bot_id}"

    # Enable sending without modifying reading
    changed = client.patch(
        bot_url,
        headers=alice,
        json={"can_send_messages": True},
    )
    assert changed.status_code == 200
    assert changed.json()["can_read_messages"] is True
    assert changed.json()["can_send_messages"] is True

    # An admin can manage the room too
    make_admin(session_factory, "bob")
    assert client.get(url, headers=bob).status_code == 200

    # Remove access
    removed = client.delete(bot_url, headers=alice)
    assert removed.status_code == 200
    assert removed.json()["status"] == "removed"

    # Bot account still exists
    assert len(client.get("/api/bots", headers=alice).json()) == 1

    # Access record is gone
    assert client.get(url, headers=alice).json() == []
    assert client.delete(bot_url, headers=alice).status_code == 404
