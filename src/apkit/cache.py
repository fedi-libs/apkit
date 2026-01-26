from typing import Any, Generic, Optional

from .kv import KT, VT, KeyValueStore


class Cache(Generic[KT, VT]):
    """
    A generic cache wrapper that uses a KeyValueStore as a backend.
    """

    def __init__(self, store: Optional[KeyValueStore[KT, Any]]):
        self._store = store

    def get(self, key: KT) -> VT | None:
        """
        Gets an item from the cache, returning None if it's expired or doesn't exist.
        """
        if self._store:
            return self._store.get(key)
        return None

    def set(self, key: KT, value: VT, ttl: float | None) -> None:
        """
        Sets an item in the cache with a specific Time-To-Live (TTL) in seconds.
        If ttl is None, the item will not expire.
        """
        if self._store:
            if ttl is not None and ttl <= 0:
                self._store.delete(key)
                return

            ttl_int = int(ttl) if ttl is not None else None
            if ttl is not None and ttl > 0 and ttl_int == 0:
                ttl_int = 1

            self._store.set(key, value, ttl_seconds=ttl_int)

    def delete(self, key: KT) -> None:
        """Deletes an item from the cache."""
        if self._store:
            self._store.delete(key)

    def exists(self, key: KT) -> bool:
        """
        Checks if a non-expired item exists in the cache.
        """
        if self._store:
            return self._store.exists(key)
        return False

    async def async_get(self, key: KT) -> VT | None:
        """
        Gets an item from the cache, returning None if it's expired or doesn't exist.
        """
        if self._store:
            return await self._store.async_get(key)
        return None

    async def async_set(self, key: KT, value: VT, ttl: float | None) -> None:
        """
        Sets an item in the cache with a specific Time-To-Live (TTL) in seconds.
        If ttl is None, the item will not expire.
        """
        if self._store:
            if ttl is not None and ttl <= 0:
                await self._store.async_delete(key)
                return

            ttl_int = int(ttl) if ttl is not None else None
            if ttl is not None and ttl > 0 and ttl_int == 0:
                ttl_int = 1

            await self._store.async_set(key, value, ttl_seconds=ttl_int)

    async def async_delete(self, key: KT) -> None:
        """Deletes an item from the cache."""
        if self._store:
            await self._store.async_delete(key)

    async def async_exists(self, key: KT) -> bool:
        """
        Checks if a non-expired item exists in the cache.
        """
        if self._store:
            return await self._store.async_exists(key)
        return False
