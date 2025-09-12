from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


class KeyValueStore(ABC, Generic[KT, VT]):
    """An abstract base class for Key-Value stores."""

    @abstractmethod
    def get(self, key: KT) -> VT | None:
        """Gets a value from the store."""
        raise NotImplementedError

    @abstractmethod
    def set(self, key: KT, value: VT, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the store."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: KT) -> None:
        """Deletes a key from the store."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: KT) -> bool:
        """Checks if a key exists in the store."""
        raise NotImplementedError

    @abstractmethod
    async def async_get(self, key: KT) -> VT | None:
        """Gets a value from the store."""
        raise NotImplementedError

    @abstractmethod
    async def async_set(self, key: KT, value: VT, ttl_seconds: int | None = 3600) -> None:
        """Sets a value in the store."""
        raise NotImplementedError

    @abstractmethod
    async def async_delete(self, key: KT) -> None:
        """Deletes a key from the store."""
        raise NotImplementedError

    @abstractmethod
    async def async_exists(self, key: KT) -> bool:
        """Checks if a key exists in the store."""
        raise NotImplementedError
