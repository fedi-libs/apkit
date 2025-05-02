import asyncio
from enum import Enum
from typing import Any, Dict, Optional

from apsig.draft import Signer as DraftSigner
import aiohttp
from cryptography.hazmat.primitives.asymmetric import rsa

from ._version import __version__

class SigType(Enum):
    DRAFT = "draft"
    LD = "ld"
    PROOF = "proof"


class ApRequest:
    def __init__(
        self,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        sig_type: SigType = SigType.DRAFT,
    ) -> None:
        self.key_id = key_id
        self.private_key = private_key
        self.sig_type = sig_type

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=loop)

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

    async def signed_post(
        self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> aiohttp.ClientResponse:
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

        response = await self._session.post(url, json=data, headers=headers)

        return response

    async def signed_get(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> aiohttp.ClientResponse:
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
            )
            headers = signer.sign()

        response = await self._session.get(url, headers=headers)

        return response
