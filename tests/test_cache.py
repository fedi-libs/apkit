import time
from typing import Any
import pytest

from apkit.kv import KeyValueStore
from apkit.cache import Cache


class FakeKeyValueStore(KeyValueStore[Any, Any]):
    """Minimal in-memory KeyValueStore for tests."""

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)

    def exists(self, key):
        return key in self._data

    async def async_get(self, key):
        return self.get(key)

    async def async_set(self, key, value):
        self.set(key, value)

    async def async_delete(self, key):
        self.delete(key)

    async def async_exists(self, key):
        return self.exists(key)

@pytest.fixture
def store():
    return FakeKeyValueStore()


@pytest.fixture
def cache(store):
    return Cache(store)


def test_set_and_get_without_ttl(cache):
    cache.set("a", "value", ttl=None)
    assert cache.get("a") == "value"


def test_set_and_get_with_ttl_not_expired(cache, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000.0)
    cache.set("a", "value", ttl=10)

    monkeypatch.setattr(time, "time", lambda: 1005.0)
    assert cache.get("a") == "value"


def test_get_expired_item(cache, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000.0)
    cache.set("a", "value", ttl=5)

    monkeypatch.setattr(time, "time", lambda: 1006.0)
    assert cache.get("a") is None
    assert not cache.exists("a")


def test_set_with_non_positive_ttl_deletes(cache):
    cache.set("a", "value", ttl=0)
    assert cache.get("a") is None

    cache.set("b", "value", ttl=-5)
    assert cache.get("b") is None


def test_delete(cache):
    cache.set("a", "value", ttl=None)
    cache.delete("a")
    assert cache.get("a") is None


def test_exists_true(cache):
    cache.set("a", "value", ttl=None)
    assert cache.exists("a") is True


def test_exists_false_for_missing_key(cache):
    assert cache.exists("missing") is False


def test_exists_false_for_expired_item(cache, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000.0)
    cache.set("a", "value", ttl=1)

    monkeypatch.setattr(time, "time", lambda: 1002.0)
    assert cache.exists("a") is False


@pytest.mark.asyncio
async def test_async_set_and_get(cache):
    await cache.async_set("a", "value", ttl=None)
    result = await cache.async_get("a")
    assert result == "value"


@pytest.mark.asyncio
async def test_async_get_expired(cache, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000.0)
    await cache.async_set("a", "value", ttl=1)

    monkeypatch.setattr(time, "time", lambda: 1002.0)
    assert await cache.async_get("a") is None


@pytest.mark.asyncio
async def test_async_exists(cache):
    await cache.async_set("a", "value", ttl=None)
    assert await cache.async_exists("a") is True


@pytest.mark.asyncio
async def test_async_delete(cache):
    await cache.async_set("a", "value", ttl=None)
    await cache.async_delete("a")
    assert await cache.async_get("a") is None
