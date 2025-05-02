from typing import Optional

from redis import asyncio as aioredis

from ..base import BaseStore

class RedisStore(BaseStore):
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, db: int = 0, password: Optional[str] = None):
        super().__init__()
        self.redis = aioredis.from_url(f"redis://{password + "@" if password else ""}{host}:{port}/{db}") # host=host, port=port, db=db, password=password

    async def set(self, key, value): 
        await self.redis.set(f"apkit:{key}", value, ex=86400)

    async def rm(self, key): 
        await self.redis.delete(f"apkit:{key}")

    async def get(self, key): 
        return await self.redis.get(f"apkit:{key}")