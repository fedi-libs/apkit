from typing import Optional, Any
import asyncio

from ..base import BaseStore

class InMemoryStore(BaseStore):
    def __init__(self):
        super().__init__()
        self.store = {}
        self.lock = asyncio.Lock()

    async def set(self, key: str, value: Any):
        async with self.lock:
            self.store[f"apkit:{key}"] = value

    async def rm(self, key: str):
        async with self.lock:
            self.store.pop(f"apkit:{key}", None)

    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            return self.store.get(f"apkit:{key}")
