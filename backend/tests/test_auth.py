import pytest

from charissa.api.auth import require_api_key
from fastapi import HTTPException


def test_no_keys_configured_allows_any_request(monkeypatch):
    monkeypatch.delenv("API_KEYS", raising=False)
    require_api_key(x_api_key=None)  # should not raise


def test_missing_key_rejected_when_keys_configured(monkeypatch):
    monkeypatch.setenv("API_KEYS", "secret-1,secret-2")
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(x_api_key=None)
    assert exc_info.value.status_code == 401


def test_wrong_key_rejected(monkeypatch):
    monkeypatch.setenv("API_KEYS", "secret-1,secret-2")
    with pytest.raises(HTTPException):
        require_api_key(x_api_key="not-a-real-key")


def test_valid_key_accepted(monkeypatch):
    monkeypatch.setenv("API_KEYS", "secret-1,secret-2")
    require_api_key(x_api_key="secret-2")  # should not raise
