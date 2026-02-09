import asyncio
from typing import Any

import aiohttp

from ..base.context import (
    BaseReqContextManagerDef,
    BaseReqContextManagerImpl,
)
from ..types import T, UnifiedResponse, UnifiedResponseAsync


class GetReqContextManager(
    BaseReqContextManagerImpl, BaseReqContextManagerDef[T]
):
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
        headers = self._reconstruct_headers(self._body)
        _, headers = await asyncio.to_thread(
            self._sign_request, headers=headers, as_dict=True
        )
        self._resp = await self._client_async.get(
            self._url,
            headers=headers,
            allow_redirects=self._allow_redirect,
            max_redirects=self._max_redirects,
            **self._kwargs,
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
        headers = self._reconstruct_headers(self._body)
        _, headers = self._sign_request(headers=headers, as_dict=False)
        self._resp = self._client.get(
            self._url,
            headers=headers,
            follow_redirects=self._allow_redirect,
            **self._kwargs,
        )
        return UnifiedResponse(self._resp)

    def __exit__(self, *args: Any) -> None:
        if self._resp:
            self._resp.close()
            self._resp = None
