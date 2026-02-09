import datetime
import json
import urllib.parse
import warnings
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    Union,
    get_args,
)

import aiohttp
import apmodel
import apsig
import httpx
from apmodel.types import ActivityPubModel
from apsig import draft
from apsig.rfc9421 import RFC9421Signer
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from ..._version import __version__
from ...types import ActorKey
from .._common import reconstruct_headers
from ..types import UnifiedResponse, UnifiedResponseAsync

T = TypeVar("T", httpx.Response, aiohttp.ClientResponse, covariant=True)

SignMethod = Literal["draft-cavage", "rfc9421", "rsa2017", "fep8b32"]

SIGN_METHOD_OPTIONS = get_args(SignMethod)
ALLOWED_SIGN_METHODS = frozenset(SIGN_METHOD_OPTIONS)
MAX_ALLOWED = len(SIGN_METHOD_OPTIONS)
EXCLUSIVE_SET = {"draft-9421": frozenset({"rfc9421", "draft-cavage"})}


class BaseReqContextManagerDef(Protocol[T]):
    async def __aenter__(self) -> UnifiedResponseAsync: ...

    async def __aexit__(self, *args: Any) -> None: ...

    def __enter__(self) -> UnifiedResponse: ...

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
        self._sign_as = set(sign_as) if sign_as else set()

        self._resp: Optional[Union[httpx.Response, aiohttp.ClientResponse]] = (
            None
        )
        self._body: Optional[Union[ActivityPubModel, Dict[str, Any], bytes]] = (
            None
        )
        self._kwargs = kwargs
        self.__validate_sign_with(sign_with=sign_with)

    def __validate_sign_with(self, sign_with: Optional[List[SignMethod]]):
        raw_input = sign_with if sign_with is not None else ["draft-cavage"]
        filtered_set = set(raw_input) & ALLOWED_SIGN_METHODS

        conflict_draft = EXCLUSIVE_SET["draft-9421"]
        if conflict_draft.issubset(filtered_set):
            filtered_set -= conflict_draft
            warnings.warn(
                "RFC9421 and draft-cavage are exclusive. Both were removed for safety.",
                UserWarning,
            )

        self._sign_with: Set[SignMethod] = filtered_set

    def _reconstruct_headers(
        self,
        body: Optional[Union[ActivityPubModel, Dict[str, Any], bytes]] = None,
    ) -> Dict[str, str]:
        return reconstruct_headers(self._headers, self._user_agent, body)

    def _sign_request(
        self, headers: Dict[str, str], as_dict: bool = False
    ) -> Tuple[Optional[Union[bytes, Dict[str, Any]]], Dict[str, str]]:
        if not self._sign_as:
            return None, headers

        sign_with = self._sign_with
        url = self._url

        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname or ""
        path = parsed_url.path or "/"

        done = {m: False for m in ["cavage", "rsa2017", "fep8b32", "rfc9421"]}

        is_rfc = "rfc9421" in sign_with
        is_cavage = "draft-cavage" in sign_with
        if is_rfc and is_cavage:
            warnings.warn(
                "Draft and RFC9421 Signing is exclusive. Legacy Draft mode prioritized.",
                UserWarning,
            )
            is_rfc = False

        if isinstance(self._body, ActivityPubModel):
            body_dict = apmodel.to_dict(self._body)
        elif isinstance(self._body, bytes):
            body_dict = json.loads(self._body)
        else:
            body_dict = self._body or {}

        if isinstance(self._body, bytes):
            body_bytes = self._body
        else:
            body_bytes = json.dumps(body_dict, ensure_ascii=False).encode(
                "utf-8"
            )

        for actor in self._sign_as:
            priv_key = actor.private_key
            key_id = actor.key_id
            if isinstance(priv_key, RSAPrivateKey):
                if is_rfc and not done["rfc9421"]:
                    rfc_signer = RFC9421Signer(priv_key, key_id)
                    headers = rfc_signer.sign(
                        headers=dict(headers),
                        method="POST",
                        host=hostname,
                        path=path,
                        body=body_bytes,
                    )
                    done["rfc9421"] = True

                if is_cavage and not done["cavage"]:
                    signer = draft.Signer(
                        headers=dict(headers),
                        method="POST",
                        url=url,
                        key_id=key_id,
                        private_key=priv_key,
                        body=body_bytes,
                    )
                    headers = signer.sign()
                    done["cavage"] = True

                if "rsa2017" in sign_with and body_dict and not done["rsa2017"]:
                    ld_signer = apsig.LDSignature()
                    body_dict = ld_signer.sign(
                        doc=body_dict,
                        creator=key_id,
                        private_key=priv_key,
                    )
                    done["rsa2017"] = True

            elif isinstance(priv_key, Ed25519PrivateKey):
                if "fep8b32" in sign_with and body_dict and not done["fep8b32"]:
                    now = (
                        datetime.datetime.now(datetime.timezone.utc)
                        .isoformat(timespec="seconds")
                        .replace("+00:00", "Z")
                    )
                    fep_signer = apsig.ProofSigner(private_key=priv_key)
                    body_dict = fep_signer.sign(
                        unsecured_document=body_dict,
                        options={
                            "type": "DataIntegrityProof",
                            "cryptosuite": "eddsa-jcs-2022",
                            "proofPurpose": "assertionMethod",
                            "verificationMethod": key_id,
                            "created": now,
                        },
                    )
                    done["fep8b32"] = True

        final_body = body_dict
        if not as_dict and isinstance(body_dict, dict):
            final_body = json.dumps(body_dict, ensure_ascii=False).encode(
                "utf-8"
            )

        return final_body, headers
