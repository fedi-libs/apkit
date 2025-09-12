import pickle
from typing import Any

from redis.asyncio import Redis as AsyncRedis
from redis.client import Redis as SyncRedis

from . import KeyValueStore


class RedisKV(KeyValueStore[Any, Any]):
    """
    A Redis-based key-value store implementation.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        **kwargs,
    ):
        self.redis = SyncRedis(host=host, port=port, db=db, password=password, **kwargs)
        self.async_redis = AsyncRedis(host=host, port=port, db=db, password=password, **kwargs)

    def get(self, key: str) -> Any | None:
        """Gets a value from the Redis store."""
        value = self.redis.get(key)
        if value is None:
            return None
        return value

    def set(self, key: Any, value: Any, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the Redis store with an optional TTL."""
        self.redis.set(key, pickle.dumps(value), ex=ttl_seconds)

    def delete(self, key: Any) -> None:
        """Deletes a key from the Redis store."""
        self.redis.delete(key)

    def exists(self, key: Any) -> bool:
        """Checks if a key exists in the Redis store."""
        return int(self.redis.exists(key)) > 0 # pyright: ignore[reportArgumentType]

    async def async_get(self, key: Any) -> Any | None:
        """Gets a value from the Redis store asynchronously."""
        value = await self.async_redis.get(key)
        if value is None:
            return None
        return pickle.loads(value)

    async def async_set(self, key: Any, value: Any, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the Redis store asynchronously with an optional TTL."""
        await self.async_redis.set(key, pickle.dumps(value), ex=ttl_seconds)

    async def async_delete(self, key: Any) -> None:
        """Deletes a key from the Redis store asynchronously."""
        await self.async_redis.delete(key)

    async def async_exists(self, key: Any) -> bool:
        """Checks if a key exists in the Redis store asynchronously."""
        return int(await self.async_redis.exists(key)) > 0
