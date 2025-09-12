from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Generic, List, Optional, TYPE_CHECKING

from .cache import Cache
from .kv import KT, VT, KeyValueStore
from .kv.inmemory import InMemoryKV

if TYPE_CHECKING:
    from .server.types import ActorKey

@dataclass
class AppConfig(Generic[KT, VT]):
    actor_keys: Optional[Callable[[str], Awaitable[List["ActorKey"]]]] = None
    kv: KeyValueStore[KT, Any] = field(default_factory=InMemoryKV)
    cache: Cache = field(default_factory=lambda: Cache(None))

    def __post_init__(self):
        self.cache = Cache(self.kv) if self.cache._store is None else self.cache # pyright: ignore[reportAttributeAccessIssue]