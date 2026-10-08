from tests.helpers import register


def test_bot_management_api(client):
    owner = register(client, "alice")
    stranger = register(client, "bob")

    payload = {
        "username": "echo_bot",
        "display_name": "Echo Bot",
        "description": "Answers messages",
    }

    # Anonymous users cannot create bots
    assert client.post(
        "/api/bots", json=payload
    ).status_code == 401

    # Create
    created_response = client.post(
        "/api/bots",
        headers=owner,
        json=payload,
    )

    assert created_response.status_code == 201, (
        created_response.text
    )
    assert (
        created_response.headers["cache-control"]
        == "no-store"
    )

    created = created_response.json()
    bot_id = created["id"]
    first_token = created["token"]

    assert first_token.startswith("lsg_")

    # List
    listed = client.get("/api/bots", headers=owner)

    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert "token" not in listed.json()[0]

    assert client.get(
        "/api/bots", headers=stranger
    ).json() == []

    # Duplicate username
    assert client.post(
        "/api/bots", headers=owner, json=payload
    ).status_code == 409

    # Another user cannot modify this bot
    assert client.patch(
        f"/api/bots/{bot_id}/status",
        headers=stranger,
        json={"is_active": False},
    ).status_code == 404

    # Rotate token
    rotated = client.post(
        f"/api/bots/{bot_id}/rotate-token",
        headers=owner,
    )

    assert rotated.status_code == 200
    assert (
        rotated.headers["cache-control"] == "no-store"
    )
    assert rotated.json()["token"] != first_token

    # Disable
    disabled = client.patch(
        f"/api/bots/{bot_id}/status",
        headers=owner,
        json={"is_active": False},
    )

    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False
