from datetime import datetime, timedelta, timezone

from jose import jwt

from auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


def test_password_hash_and_verify():
    hashed = hash_password("secret123")

    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_and_verify_token():
    token = create_access_token({"sub": "alice"})

    assert verify_token(token) == "alice"


def test_invalid_token_returns_none():
    assert verify_token("not-a-real-token") is None


def test_expired_token_returns_none():
    expired_token = jwt.encode(
        {
            "sub": "alice",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert verify_token(expired_token) is None

