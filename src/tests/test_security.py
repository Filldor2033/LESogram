import asyncio

import pytest
from starlette.requests import Request
from starlette.responses import Response

from core.security_headers import add_security_headers
from schemas import LoginRequest, RegisterRequest


def test_register_request_invalid_username_chars():
    with pytest.raises(ValueError) as exc:
        RegisterRequest(username="escapetest<script>", password="secret123")

    assert "invalid characters" in str(exc.value)


def test_login_request_invalid_username_chars():
    with pytest.raises(ValueError):
        LoginRequest(username="bob\nadmin", password="secret")


def test_security_middleware_https_headers(client):
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
    response = asyncio.run(add_security_headers(request, dummy_call_next))

    assert response.headers.get("Strict-Transport-Security") == (
        "max-age=31536000; includeSubDomains"
    )

    scope["scheme"] = "http"
    request = Request(scope)
    response = asyncio.run(add_security_headers(request, dummy_call_next))

    assert "Strict-Transport-Security" not in response.headers


def test_security_middleware_cache_control(client):
    response = client.get("/login")
    assert response.headers.get("Cache-Control") == "no-store"

    response = client.get("/register")
    assert response.headers.get("Cache-Control") == "no-store"
