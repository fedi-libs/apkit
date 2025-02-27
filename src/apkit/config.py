from aiohttp_client_cache import CacheBackend

from .store.base import BaseStore
from .store.kv.inmemory import InMemoryStore

class Config:
    allow_private_ip: bool = False
    max_redirects: int = 5
    http_cache_backend: CacheBackend | None = None
    kv: BaseStore = InMemoryStore()