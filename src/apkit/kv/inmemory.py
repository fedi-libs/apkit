import time
from typing import Any

from . import KeyValueStore


class InMemoryKV(KeyValueStore[Any, Any]):
    """
    An in-memory key-value store implementation with TTL support.
    """

    def __init__(self) -> None:
        self._store: dict[Any, tuple[Any, float | None]] = {}

    def get(self, key: Any) -> Any | None:
        """Gets a value from the in-memory store, checking for TTL."""
        if key not in self._store:
            return None

        value, expires_at = self._store[key]
        if expires_at is not None and expires_at < time.time():
            del self._store[key]
            return None

        return value

    def set(self, key: Any, value: Any, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the in-memory store with an optional TTL."""
        expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
        self._store[key] = (value, (expires_at))

    def delete(self, key: Any) -> None:
        """Deletes a key from the in-memory store."""
        if key in self._store:
            del self._store[key]

    def exists(self, key: Any) -> bool:
        """Checks if a key exists in the in-memory store, considering TTL."""
        if key not in self._store:
            return False

        _, expires_at = self._store[key]
        if expires_at is not None and expires_at < time.time():
            del self._store[key]
            return False

        return True

    async def async_get(self, key: Any) -> Any | None:
        """Gets a value from the in-memory store, checking for TTL."""
        return self.get(key)

    async def async_set(self, key: Any, value: Any, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the in-memory store with an optional TTL."""
        self.set(key, value, ttl_seconds)

    async def async_delete(self, key: Any) -> None:
        """Deletes a key from the in-memory store."""
        self.delete(key)

    async def async_exists(self, key: Any) -> bool:
        """Checks if a key exists in the in-memory store, considering TTL."""
        return self.exists(key)