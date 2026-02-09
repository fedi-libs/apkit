from typing import Any, Dict, List, Optional, Protocol, Tuple, TypeVar, Union

import aiohttp
import httpx
from apmodel.types import ActivityPubModel

from ..._version import __version__
from ...types import ActorKey
from .._common import reconstruct_headers, sign_request

T = TypeVar("T", httpx.Response, aiohttp.ClientResponse, covariant=True)

SignMethod = str


class BaseReqContextManagerDef(Protocol[T]):
    async def __aenter__(self): ...

    async def __aexit__(self, *args: Any) -> None: ...

    def __enter__(self): ...

    def __exit__(self, *args: Any) -> None: ...


class BaseReqContextManagerImpl:
    def __init__(
        self,
        client: Optional[httpx.Client],
        client_async: Optional[aiohttp.ClientSession],
        url: str,
        user_agent: str = f"apkit/{__version__}",
        headers: Optional[Dict[str, str]] = None,
        allow_redirect: bool = True,
        max_redirects: int = 10,
        sign_as: Optional[List[ActorKey]] = None,
        sign_with: Optional[List[SignMethod]] = None,
        **kwargs: Any,
    ):
        self._client = client
        self._client_async = client_async
        self._url = url
        self._user_agent = user_agent
        self._headers = headers
        self._allow_redirect = allow_redirect
        self._max_redirects = max_redirects
        self._sign_as = sign_as
        self._sign_with = sign_with
        self._kwargs = kwargs
        self._resp: Optional[Union[httpx.Response, aiohttp.ClientResponse]] = None
        self._body: Optional[Union[ActivityPubModel, Dict[str, Any], bytes]] = None

    def _reconstruct_headers(
        self, body: Optional[Union[ActivityPubModel, Dict[str, Any], bytes]] = None
    ) -> Dict[str, str]:
        return reconstruct_headers(self._headers, self._user_agent, body)

    def _sign_request(
        self, headers: Dict[str, str], as_dict: bool = False
    ) -> Tuple[Optional[Union[bytes, Dict[str, Any]]], Dict[str, str]]:
        if not self._sign_as:
            return None, headers

        sign_with_methods = self._sign_with or ["draft-cavage"]

        return sign_request(
            url=self._url,
            headers=headers,
            signatures=self._sign_as,
            body=self._body,
            sign_with=sign_with_methods,
            as_dict=as_dict,
        )
