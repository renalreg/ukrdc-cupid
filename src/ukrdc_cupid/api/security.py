"""
Configuration
-------------
    API_KEYS_FILE=/path/to/api_keys.json
"""

import hmac
import json
import logging
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _load_api_keys() -> dict[str, dict]:
    """Load {client_name: {"key": str, "scopes": set[str]}} from config.

    Raises if a file/JSON was explicitly configured but is invalid, so a
    typo fails startup loudly
    """
    file_path = os.environ.get("API_KEYS_FILE")
    if file_path:
        with open(file_path, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = json.loads(os.environ.get("API_KEYS_JSON", "{}"))

    keys: dict[str, dict] = {}
    for name, cfg in raw.items():
        key = cfg.get("key")
        if key:
            keys[name] = {"key": key, "scopes": set(cfg.get("scopes", []))}

    logger.info(f"Loaded {len(keys)} API key(s)")
    return keys


API_KEYS = _load_api_keys()


async def verify_api_key(
    request: Request,
    presented_key: str | None = Security(_api_key_header),
) -> str:
    """
    FastAPI dependency: validates X-API-Key and checks its scopes against
    the current route's `name=`. Returns the authenticated client's name
    on success (handy for logging); raises HTTPException otherwise.
    """
    if not presented_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    matched = None
    for client_name, cfg in API_KEYS.items():
        if hmac.compare_digest(presented_key, cfg["key"]):
            matched = (client_name, cfg["scopes"])
            break

    if matched is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    client_name, scopes = matched

    if "all" in scopes:
        return client_name

    route_name = getattr(request.scope.get("route"), "name", None)
    if route_name is None or route_name not in scopes:
        raise HTTPException(
            status_code=403,
            detail="This API key does not have access to this endpoint.",
        )

    return client_name