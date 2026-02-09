from typing import Any, Awaitable, Generic, Optional, Protocol, TypeVar

import aiohttp
import apmodel
import httpx
from apmodel.types import ActivityPubModel

T = TypeVar("T", httpx.Response, aiohttp.ClientResponse, covariant=True)


class Response(Protocol[T]):
    @property
    def status(self) -> int: ...

    @property
    def raw(self) -> T: ...

    def json(self, **kwargs) -> dict | Awaitable[dict]: ...

    def parse(self, **kwargs) -> ActivityPubModel | Awaitable[ActivityPubModel]: ...


class UnifiedResponse(Response):
    def __init__(self, native_response: httpx.Response):
        self._raw = native_response

    @property
    def raw(self) -> httpx.Response:
        return self._raw

    @property
    def headers(self) -> dict:
        return dict(self._raw.headers)

    @property
    def status(self) -> int:
        return self._raw.status_code

    def parse(self, **kwargs) -> Any:
        """Read the response body as an ActivityPub model."""
        json = self.json(**kwargs)
        return apmodel.load(json)

    def json(self, **kwargs) -> Any:
        return self._raw.json()

    def close(self):
        self._raw.close()


class UnifiedResponseAsync(Response):
    def __init__(self, native_response: aiohttp.ClientResponse):
        self._raw = native_response

    @property
    def raw(self) -> aiohttp.ClientResponse:
        return self._raw

    @property
    def headers(self) -> dict:
        return dict(self._raw.headers)

    @property
    def status(self) -> int:
        return self._raw.status

    async def json(
        self,
        encoding: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs,
    ) -> Any:
        return await self._raw.json(
            encoding=encoding, content_type=content_type, **kwargs
        )

    async def parse(
        self,
        encoding: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs,
    ) -> Any:
        """Read the response body as an ActivityPub model."""
        json = await self.json(
            encoding=encoding, content_type=content_type, **kwargs
        )
        return apmodel.load(json)

    async def close(self):
        await self._raw.release()


class UnifiedContextManager(Protocol[T]):
    async def __aenter__(self) -> Response[T]: ...
    async def __aexit__(self, *args: Any) -> None: ...

    def __enter__(self) -> Response[T]: ...
    def __exit__(self, *args: Any) -> None: ...
