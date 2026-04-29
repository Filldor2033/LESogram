from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from core.rate_limit import (enforce_http_rate_limit,
                             get_client_ip_from_request,
                             get_client_ip_from_websocket, rate_limiter)


def test_get_client_ip_from_request_with_none_client():
    request = Mock()
    request.client = None

    ip = get_client_ip_from_request(request)

    assert ip == "unknown"


def test_get_client_ip_from_websocket_with_none_client():
    websocket = Mock()
    websocket.client = None

    ip = get_client_ip_from_websocket(websocket)

    assert ip == "unknown"


def test_enforce_http_rate_limit_triggers(client, monkeypatch):
    mock_hit = Mock(return_value=30)
    monkeypatch.setattr(rate_limiter, "hit", mock_hit)

    request = Mock()
    request.client = Mock(host="127.0.0.1")

    with pytest.raises(HTTPException) as exc:
        enforce_http_rate_limit(
            request,
            "test_bucket",
            limit=1,
            window_seconds=60,
        )

    assert exc.value.status_code == 429
    assert "Retry in 30 seconds" in exc.value.detail
    mock_hit.assert_called_once()
