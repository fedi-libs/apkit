from typing import Any, Awaitable, Optional, Protocol, TypeVar

import aiohttp
import apmodel
import httpx
from apmodel.types import ActivityPubModel

T = TypeVar("T", httpx.Response, aiohttp.ClientResponse, covariant=True)
RT = TypeVar("RT", dict[str, Any], Awaitable[dict[str, Any]])
PT = TypeVar("PT", ActivityPubModel, Awaitable[ActivityPubModel])

class Response(Protocol[T, RT, PT]):
    @property
    def status(self) -> int: ...

    @property
    def raw(self) -> T: ...

    def json(self, **kwargs) -> RT: ...

    def parse(self, **kwargs) -> PT: ...


class UnifiedResponse(Response[httpx.Response, dict[str, Any], ActivityPubModel]):
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

    def parse(self, **kwargs) -> ActivityPubModel:
        """Read the response body as an ActivityPub model."""
        json = self.json(**kwargs)
        obj = apmodel.load(json)
        if isinstance(obj, ActivityPubModel):
            return obj
        raise ValueError("failed to parse json")

    def json(self, **kwargs) -> dict:
        return self._raw.json()


class UnifiedResponseAsync(Response[aiohttp.ClientResponse, Awaitable[dict[str, Any]], Awaitable[ActivityPubModel]]):
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
    ) -> dict:
        try:
            return await self._raw.json(
                encoding=encoding, content_type=content_type, **kwargs
            )
        finally:
            await self._raw.release()

    async def parse(
        self,
        encoding: Optional[str] = None,
        content_type: Optional[str] = "application/json",
        **kwargs,
    ) -> ActivityPubModel:
        """Read the response body as an ActivityPub model."""
        json = await self.json(
            encoding=encoding, content_type=content_type, **kwargs
        )
        obj = apmodel.load(json)
        if isinstance(obj, ActivityPubModel):
            return obj
        raise ValueError("failed to parse json")