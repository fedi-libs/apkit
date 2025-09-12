import time
from typing import Any, Generic, Optional

from .kv import KT, VT, KeyValueStore

class Cache(Generic[KT, VT]):
    """
    A generic cache wrapper that uses a KeyValueStore as a backend
    and adds Time-To-Live (TTL) support.
    """

    class _CacheItem:
        def __init__(self, value: VT, expiration: float):
            self.value = value
            self.expiration = expiration

    def __init__(self, store: Optional[KeyValueStore[KT, Any]]):
        self._store = store

    def get(self, key: KT) -> VT | None:
        """
        Gets an item from the cache, returning None if it's expired or doesn't exist.
        """
        if self._store:
            item = self._store.get(key)
            if not isinstance(item, self._CacheItem):
                return None

            if time.time() > item.expiration:
                self._store.delete(key)
                return None

            return item.value

    def set(self, key: KT, value: VT, ttl: float | None) -> None:
        """
        Sets an item in the cache with a specific Time-To-Live (TTL) in seconds.
        If ttl is None, the item will not expire.
        """
        if self._store:
            if ttl is not None:
                if ttl <= 0:
                    self._store.delete(key)
                    return
                expiration = time.time() + ttl
            else:
                expiration = float("inf")

            self._store.set(key, self._CacheItem(value, expiration))

    def delete(self, key: KT) -> None:
        """Deletes an item from the cache."""
        if self._store:
            self._store.delete(key)

    def exists(self, key: KT) -> bool:
        """
        Checks if a non-expired item exists in the cache.
        """
        if self._store:
            item = self._store.get(key)
            if not isinstance(item, self._CacheItem):
                return False

            if time.time() > item.expiration:
                self._store.delete(key)
                return False

            return True
        else:
            return False

    async def async_get(self, key: KT) -> VT | None:
        """
        Gets an item from the cache, returning None if it's expired or doesn't exist.
        """
        if self._store:
            item = self._store.get(key)
            if not isinstance(item, self._CacheItem):
                return None

            if time.time() > item.expiration:
                self._store.delete(key)
                return None

            return item.value

    async def async_set(self, key: KT, value: VT, ttl: float | None) -> None:
        """
        Sets an item in the cache with a specific Time-To-Live (TTL) in seconds.
        If ttl is None, the item will not expire.
        """
        if self._store:
            if ttl is not None:
                if ttl <= 0:
                    self._store.delete(key)
                    return
                expiration = time.time() + ttl
            else:
                expiration = float("inf")

            self._store.set(key, self._CacheItem(value, expiration))

    async def async_delete(self, key: KT) -> None:
        """Deletes an item from the cache."""
        if self._store:
            self._store.delete(key)

    async def async_exists(self, key: KT) -> bool:
        """
        Checks if a non-expired item exists in the cache.
        """
        if self._store:
            item = self._store.get(key)
            if not isinstance(item, self._CacheItem):
                return False

            if time.time() > item.expiration:
                self._store.delete(key)
                return False

            return True
        return False