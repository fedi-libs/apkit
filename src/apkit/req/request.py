import ipaddress
import json
from typing import Optional

import aiohttp
from apsig.draft.sign import draftSigner
from cryptography.hazmat.primitives.asymmetric import rsa

from ..config import Config


class APRequest:
    def __init__(self, config: Config):
        self.config: Config = config
        self.signer: draftSigner = draftSigner()

    def __check_private(self, ip: str) -> bool:
        if self.config.allow_private_ip:
            return False
        else:
            if ip == "localhost":
                return True
            elif ip.endswith(".local"):
                return True
            elif ip.endswith(".localhost"):
                return True
            try:
                return ipaddress.ip_address(ip).is_private
            except ValueError:
                return False

    async def get(
        self,
        url: Optional[str], # type: ignore
        headers: dict = {},
        private_key: Optional[rsa.RSAPrivateKey] = None,
        key_id: Optional[str] = None,
    ) -> Optional[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session:
            if isinstance(url, str):
                if self.__check_private(url):
                    raise Exception
                if private_key and key_id:
                    headers = self.signer.sign(private_key, "GET", url, headers, key_id)
                redirects = 0
                while redirects < self.config.max_redirects:
                    try:
                        async with session.get(
                            url, allow_redirects=False, headers=headers
                        ) as resp:  # type: ignore
                            if resp.status in (301, 302):
                                url: Optional[str] = resp.headers.get("Location")
                                if url:
                                    if self.__check_private(url):  # type: ignore
                                        raise
                                redirects += 1
                            else:
                                return resp
                    except Exception:
                        return None
                return None

    async def post(
        self,
        url: Optional[str], # type: ignore
        body: dict,
        headers: dict = {"Content-Type": "application/activity+json"},
        private_key: Optional[rsa.RSAPrivateKey] = None,
        key_id: Optional[str] = None,
    ):
        async with aiohttp.ClientSession() as session:
            if isinstance(url, str):
                body_encoded = json.dumps(body).encode("utf-8")
                if self.__check_private(url):
                    raise Exception
                if private_key and key_id:
                    headers = self.signer.sign(
                        private_key, "POST", url, headers, key_id, body=body_encoded
                    )
                redirects = 0
                while redirects < self.config.max_redirects:
                    try:
                        async with session.get(
                            url, allow_redirects=False, headers=headers, json=body
                        ) as resp:  # type: ignore
                            if resp.status in (301, 302):
                                url: Optional[str] = resp.headers.get("Location")
                                if url:
                                    if self.__check_private(url):  # type: ignore
                                        raise
                                redirects += 1
                            else:
                                return resp
                    except Exception:
                        return None
                return None
