from __future__ import annotations

import asyncio
from enum import Enum
from typing import Any, Dict, Optional

from apsig.draft import Signer as DraftSigner
import aiohttp
from cryptography.hazmat.primitives.asymmetric import rsa

from ._version import __version__
from .config import Config
from .exceptions import RedirectLimitError

class SigType(Enum):
    DRAFT = "draft"
    LD = "ld"
    PROOF = "proof"


class ApRequest:
    def __init__(
        self,
        config: Config = Config(),
        sig_type: SigType = SigType.DRAFT,
        key_id: Optional[str] = None,
        private_key: Optional[rsa.RSAPrivateKey] = None,
    ) -> None:
        self.config: Config = config
        self.key_id = key_id
        self.private_key = private_key
        self.sig_type = sig_type

        self.__redirect_count = 0

    async def __aenter__(self) -> ApRequest:
        loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=loop)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.__redirect_count = 0
        await self._session.close()

    async def _handle_redirect(
        self, response: aiohttp.ClientResponse, method: str, data: Optional[Dict[str, Any]] = None, redirect_count: int = 0
    ) -> aiohttp.ClientResponse:
        if self.__redirect_count >= self.config.max_redirects:
            raise RedirectLimitError()

        if response.status in (301, 302, 307, 308):
            location = response.headers.get('Location')
            if location:
                if method == "GET":
                    self.__redirect_count = self.__redirect_count + 1
                    return await self.signed_get(location)
                elif method == "POST":
                    self.__redirect_count = self.__redirect_count + 1
                    return await self.signed_post(location, data or {})
        return response

    async def signed_post(
        self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> aiohttp.ClientResponse:
        if self.private_key is None or self.key_id is None:
            raise ValueError("Private key and key ID must be set for signing.")

        if headers is None:
            headers = {
                "Content-Type": "application/activity+json",
                "Accept": "application/activity+json",
                "User-Agent": f"apkit/{__version__}",
            }

        if self.sig_type == SigType.DRAFT:
            signer = DraftSigner(
                headers=headers,
                private_key=self.private_key,
                method="POST",
                url=url,
                key_id=self.key_id,
                body=data,
            )
            headers = signer.sign()

        response = await self._session.post(url, json=data, headers=headers, allow_redirects=False)
        return await self._handle_redirect(response, "POST", data)

    async def signed_get(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> aiohttp.ClientResponse:
        if headers is None:
            headers = {
                "Content-Type": "application/activity+json",
                "Accept": "application/activity+json",
                "User-Agent": f"apkit/{__version__}",
            }
        if self.private_key and self.key_id:
            if self.sig_type == SigType.DRAFT:
                signer = DraftSigner(
                    headers=headers,
                    private_key=self.private_key,
                    method="POST",
                    url=url,
                    key_id=self.key_id,
                )
                headers = signer.sign()

        response = await self._session.get(url, headers=headers, allow_redirects=False)
        return await self._handle_redirect(response, "GET", None)
