import asyncio
from typing import Any, Dict, List, Optional

import aiohttp
import httpx
from apmodel.types import ActivityPubModel

from ..._version import __version__
from ...types import ActorKey
from ..base.context import (
    BaseReqContextManagerDef,
    BaseReqContextManagerImpl,
    SignMethod,
)
from ..types import T, UnifiedResponse, UnifiedResponseAsync


class PostReqContextManager(
    BaseReqContextManagerImpl, BaseReqContextManagerDef[T]
):
    def __init__(
        self,
        client: Optional[httpx.Client],
        client_async: Optional[aiohttp.ClientSession],
        url: str,
        user_agent: str = f"apkit/{__version__}",
        headers: Optional[Dict[str, str]] = None,
        json: Optional[ActivityPubModel | Dict[str, Any]] = None,
        allow_redirect: bool = True,
        max_redirects: int = 10,
        sign_as: Optional[List[ActorKey]] = None,
        sign_with: Optional[List[SignMethod]] = None,
        **kwargs: Any,
    ):
        super().__init__(
            client,
            client_async,
            url,
            user_agent,
            headers,
            allow_redirect,
            max_redirects,
            sign_as,
            sign_with,
            **kwargs,
        )
        self._body = json

    async def __aenter__(self) -> UnifiedResponseAsync:
        if self._resp:
            raise RuntimeError(
                f"{self.__class__.__name__} instance cannot be reused. "
                "Each request requires a new context manager instance."
            )
        if not self._client_async or self._client_async.closed:
            raise RuntimeError(
                "The async client session is not initialized or has been closed. "
                "Ensure you are using 'async with ActivityPubClient()'."
            )
        args: Dict[str, Any] = {}
        headers = self._reconstruct_headers(self._body)
        body, headers = await asyncio.to_thread(
            self._sign_request, headers=headers, as_dict=True
        )
        if body:
            if isinstance(body, dict):
                args["json"] = body
            else:
                args["data"] = body
        self._resp = await self._client_async.post(
            self._url,
            headers=headers,
            allow_redirects=self._allow_redirect,
            **self._kwargs | args,
        )
        return UnifiedResponseAsync(self._resp)

    async def __aexit__(self, *args: Any) -> None:
        if (
            self._resp
            and isinstance(self._resp, aiohttp.ClientResponse)
            and not self._resp.closed
        ):
            self._resp.close()
            self._resp = None

    def __enter__(self) -> UnifiedResponse:
        if self._resp:
            raise RuntimeError(
                f"{self.__class__.__name__} instance cannot be reused. "
                "Each request requires a new context manager instance."
            )
        if not self._client:
            raise RuntimeError(
                "The client session is not initialized or has been closed. "
                "Ensure you are using 'with ActivityPubClient()'."
            )
        args: Dict[str, Any] = {}
        headers = self._reconstruct_headers(self._body)
        body, headers = self._sign_request(
            headers=headers, as_dict=not isinstance(self._body, bytes)
        )
        if body:
            if isinstance(body, dict):
                args["json"] = body
            else:
                args["data"] = body
        self._resp = self._client.post(
            self._url,
            headers=headers,
            follow_redirects=self._allow_redirect,
            **self._kwargs | args,
        )
        return UnifiedResponse(self._resp)

    def __exit__(self, *args: Any) -> None:
        if self._resp:
            self._resp.close()
            self._resp = None
