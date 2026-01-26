import time
from collections import OrderedDict
from typing import Any

from . import KeyValueStore


class InMemoryKV(KeyValueStore[Any, Any]):
    """
    An in-memory key-value store implementation with TTL and LRU support.
    """

    def __init__(self) -> None:
        self._store: dict[Any, tuple[Any, float | None]] = {}
        self._lru_configs: dict[str, int | None] = {}
        self._lru_keys: dict[str, OrderedDict[Any, None]] = {}

    def configure_lru(self, namespace: str, max_size: int | None = None) -> None:
        """Configures LRU settings for a specific namespace."""
        self._lru_configs[namespace] = max_size
        if namespace not in self._lru_keys:
            self._lru_keys[namespace] = OrderedDict()
        
        if max_size is not None:
            self._enforce_lru(namespace, max_size)

    def _get_namespace(self, key: Any) -> str:
        if isinstance(key, str) and ":" in key:
            return key.split(":", 1)[0]
        return "default"

    def _update_lru_on_access(self, key: Any) -> None:
        namespace = self._get_namespace(key)
        if namespace in self._lru_keys and key in self._lru_keys[namespace]:
            self._lru_keys[namespace].move_to_end(key)

    def _update_lru_on_set(self, key: Any) -> None:
        namespace = self._get_namespace(key)
        max_size = self._lru_configs.get(namespace)
        
        if namespace not in self._lru_keys:
             self._lru_keys[namespace] = OrderedDict()
             
        self._lru_keys[namespace][key] = None
        self._lru_keys[namespace].move_to_end(key)
        
        if max_size is not None:
            self._enforce_lru(namespace, max_size)

    def _remove_from_lru(self, key: Any) -> None:
        namespace = self._get_namespace(key)
        if namespace in self._lru_keys and key in self._lru_keys[namespace]:
            del self._lru_keys[namespace][key]

    def _enforce_lru(self, namespace: str, max_size: int) -> None:
        keys = self._lru_keys.get(namespace)
        if keys is None:
            return
            
        while len(keys) > max_size:
            oldest_key, _ = keys.popitem(last=False)
            if oldest_key in self._store:
                del self._store[oldest_key]

    def get(self, key: Any) -> Any | None:
        """Gets a value from the in-memory store, checking for TTL."""
        if key not in self._store:
            return None

        value, expires_at = self._store[key]
        if expires_at is not None and expires_at < time.time():
            self.delete(key)
            return None

        self._update_lru_on_access(key)
        return value

    def set(self, key: Any, value: Any, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the in-memory store with an optional TTL."""
        expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
        self._store[key] = (value, expires_at)
        self._update_lru_on_set(key)

    def delete(self, key: Any) -> None:
        """Deletes a key from the in-memory store."""
        if key in self._store:
            del self._store[key]
        self._remove_from_lru(key)

    def exists(self, key: Any) -> bool:
        """Checks if a key exists in the in-memory store, considering TTL."""
        if key not in self._store:
            return False

        _, expires_at = self._store[key]
        if expires_at is not None and expires_at < time.time():
            self.delete(key)
            return False

        self._update_lru_on_access(key)
        return True

    async def async_get(self, key: Any) -> Any | None:
        """Gets a value from the in-memory store, checking for TTL."""
        return self.get(key)

    async def async_set(
        self, key: Any, value: Any, ttl_seconds: int | None = 3600
    ) -> None:
        """Sets a value in the in-memory store with an optional TTL."""
        self.set(key, value, ttl_seconds)

    async def async_delete(self, key: Any) -> None:
        """Deletes a key from the in-memory store."""
        self.delete(key)

    async def async_exists(self, key: Any) -> bool:
        """Checks if a key exists in the in-memory store, considering TTL."""
        return self.exists(key)