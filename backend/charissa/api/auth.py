import os

from fastapi import Header, HTTPException, status


def _valid_keys() -> set[str]:
    raw = os.environ.get("API_KEYS", "")
    return {key.strip() for key in raw.split(",") if key.strip()}


def require_api_key(x_api_key: str | None = Header(default=None)):
    """Gate access behind a shared API key.

    If API_KEYS is unset, auth is a no-op — keeps local dev friction-free
    while letting a real deployment require it by setting the env var.
    """
    keys = _valid_keys()
    if not keys:
        return
    if x_api_key not in keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
