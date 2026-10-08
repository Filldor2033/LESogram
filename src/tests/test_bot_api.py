from tests.helpers import register


def create_test_bot(client):
    owner = register(client, "alice")

    response = client.post(
        "/api/bots",
        headers=owner,
        json={
            "username": "echo_bot",
            "display_name": "Echo Bot",
            "description": "Test bot",
        },
    )

    assert response.status_code == 201, response.text

    return owner, response.json()


def bot_headers(token: str):
    return {
        "Authorization": f"Bot {token}"
    }


def test_get_me(client):
    owner, bot = create_test_bot(client)

    response = client.get(
        "/api/bot/getMe",
        headers=bot_headers(bot["token"]),
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["ok"] is True
    assert data["result"]["bot_id"] == bot["id"]
    assert data["result"]["username"] == "echo_bot"
    assert data["result"]["display_name"] == "Echo Bot"
    assert data["result"]["is_bot"] is True
    assert "token" not in data["result"]
    assert "token_hash" not in data["result"]
    assert "owner_id" not in data["result"]


def test_invalid_authentication(client):
    owner, bot = create_test_bot(client)

    # Missing token
    assert client.get(
        "/api/bot/getMe"
    ).status_code == 401

    # Invalid token
    assert client.get(
        "/api/bot/getMe",
        headers=bot_headers("invalid_token"),
    ).status_code == 401

    # Human JWT is not a bot token
    assert client.get(
        "/api/bot/getMe",
        headers=owner,
    ).status_code == 401

    # Bot token cannot access human endpoints
    assert client.get(
        "/api/bots",
        headers=bot_headers(bot["token"]),
    ).status_code == 401


def test_token_rotation(client):
    owner, bot = create_test_bot(client)

    old_token = bot["token"]

    rotated = client.post(
        f"/api/bots/{bot['id']}/rotate-token",
        headers=owner,
    )

    assert rotated.status_code == 200
    new_token = rotated.json()["token"]

    # Previous token must stop working
    assert client.get(
        "/api/bot/getMe",
        headers=bot_headers(old_token),
    ).status_code == 401

    # New token works
    assert client.get(
        "/api/bot/getMe",
        headers=bot_headers(new_token),
    ).status_code == 200


def test_disabled_bot(client):
    owner, bot = create_test_bot(client)

    client.patch(
        f"/api/bots/{bot['id']}/status",
        headers=owner,
        json={"is_active": False},
    )

    assert client.get(
        "/api/bot/getMe",
        headers=bot_headers(bot["token"]),
    ).status_code == 401
