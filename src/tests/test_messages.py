import pytest
from fastapi import HTTPException

from core.config import MAX_MESSAGE_LENGTH
from services.messages import normalize_message_text


def test_normalize_message_text_too_long():
    long_text = "x" * (MAX_MESSAGE_LENGTH + 1)

    with pytest.raises(HTTPException) as exc:
        normalize_message_text(long_text, allow_empty=False)

    assert exc.value.status_code == 400
    assert "at most" in exc.value.detail


def test_normalize_message_text_empty_not_allowed():
    with pytest.raises(HTTPException) as exc:
        normalize_message_text("   ", allow_empty=False)

    assert exc.value.status_code == 400
    assert "cannot be empty" in exc.value.detail


def test_normalize_message_text_empty_allowed():
    result = normalize_message_text("  \n  ", allow_empty=True)

    assert result == ""
