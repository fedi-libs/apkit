from typing import Any, Dict, List, Optional

import aiohttp
import httpx
from apmodel.types import ActivityPubModel

from .._version import __version__
from ..types import ActorKey
from .base.context import SignMethod
from .methods.get import GetReqContextManager
from .methods.post import PostReqContextManager


class ActivityPubClient:
    def __init__(self, user_agent: str = f"apkit/{__version__}"):
        self.__user_agent = user_agent

        self.__aiohttp: Optional[aiohttp.ClientSession] = None
        self.__httpx: Optional[httpx.Client] = None


    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        allow_redirect: bool = True,
        max_redirects: int = 10,
        sign_as: Optional[List[ActorKey]] = None,
        sign_with: Optional[List[SignMethod]] = None,
    ) -> GetReqContextManager:
        return GetReqContextManager(
            self.__httpx,
            self.__aiohttp,
            url,
            self.__user_agent,
            headers,
            allow_redirect,
            max_redirects,
            sign_as,
            sign_with,
        )

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[ActivityPubModel | dict[str, Any]] = None,
        allow_redirect: bool = True,
        max_redirects: int = 10,
        sign_as: Optional[List[ActorKey]] = None,
        sign_with: Optional[List[SignMethod]] = None,
    ) -> PostReqContextManager:
        return PostReqContextManager(
            self.__httpx,
            self.__aiohttp,
            url,
            self.__user_agent,
            headers,
            json,
            allow_redirect,
            max_redirects,
            sign_as,
            sign_with,
        )

    async def __aenter__(self):
        if self.__aiohttp is None or self.__aiohttp.closed:
            self.__aiohttp = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.__aiohttp and not self.__aiohttp.closed:
            await self.__aiohttp.close()

    def __enter__(self):
        if not self.__httpx:
            self.__httpx = httpx.Client()
        return self

    def __exit__(self, *args):
        if self.__httpx:
            self.__httpx.close()