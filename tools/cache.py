import json
from typing import Any, Optional
from config import redis_client
import logging

logger = logging.getLogger(__name__)


def cache_set(key: str, value: Any, ttl_seconds: int | None = 3600) -> bool:
    """
    Store JSON-serializable data in Redis under `key`.
    ttl_seconds: time-to-live in seconds. Use None for persistent key.
    """
    try:
        payload = json.dumps(value, default=str)
        if ttl_seconds:
            redis_client.set(key, payload, ex=ttl_seconds)
        else:
            redis_client.set(key, payload)
        return True
    except Exception as e:
        logger.exception("Failed to set cache for key %s: %s", key, e)
        return False


def cache_get(key: str) -> Optional[Any]:
    """
    Return parsed JSON value or None if missing.
    """
    try:
        val = redis_client.get(key)
        if not val:
            return None
        return json.loads(val)
    except Exception as e:
        logger.exception("Failed to get cache for key %s: %s", key, e)
        return None


def cache_delete(key: str) -> bool:
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.exception("Failed to delete cache key %s: %s", key, e)
        return False
