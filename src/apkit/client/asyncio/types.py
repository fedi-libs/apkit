import asyncio
from typing import Any, Coroutine, Generator, Optional, TypeVar, Union

from aiohttp.client import ClientResponse as _ClientResponse
from aiohttp.client import ClientWebSocketResponse
from aiohttp.client import _BaseRequestContextManager as _BaseRequestContextManagerOriginal
from aiohttp.typedefs import JSONDecoder, DEFAULT_JSON_DECODER
import apmodel
from apmodel.types import ActivityPubModel


class ActivityPubClientResponse(_ClientResponse):
    async def parse(
        self,
        *,
        encoding: Optional[str] = None,
        loads: JSONDecoder = DEFAULT_JSON_DECODER,
        content_type: Optional[str] = "application/json",
    ) -> Union[ActivityPubModel, dict]:
        """Read the response body as an ActivityPub model."""
        json = await self.json(encoding=encoding,loads=loads,content_type=content_type)
        return apmodel.load(json)

_RetType = TypeVar("_RetType", ActivityPubClientResponse, ClientWebSocketResponse)


class _BaseRequestContextManager(_BaseRequestContextManagerOriginal[_RetType]):
    def __init__(self, coro: Coroutine[asyncio.Future[Any], None, _RetType]) -> None:
        super().__init__(coro)

    def __await__(self) -> Generator[Any, None, _RetType]:
        return super().__await__()
    
    def __iter__(self) -> Generator[Any, None, _RetType]:
        return super().__iter__()
    
    async def __aenter__(self) -> _RetType:
        return await super().__aenter__()
    
_RequestContextManager = _BaseRequestContextManager[ActivityPubClientResponse]