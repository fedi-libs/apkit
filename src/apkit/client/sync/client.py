import datetime
import typing
from typing_extensions import Optional
import json
import warnings

import apsig
from apsig import draft
from apmodel.types import ActivityPubModel
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
import httpcore

from .actor import ActorFetcher
from .exceptions import TooManyRedirects, NotImplementedWarning
from .types import Response
from .._common import sign_request
from ...types import ActorKey
from ..._version import __version__


class ActivityPubClient:
    def __init__(self, user_agent: str = f"apkit/{__version__}") -> None:
        self.user_agent = user_agent
        self.actor: ActorFetcher = ActorFetcher(self)

        self.__http: Optional[httpcore.ConnectionPool] = None

    def __enter__(self) -> "ActivityPubClient":
        self.__http = httpcore.ConnectionPool()
        return self

    def __exit__(self, *args) -> None:
        if self.__http:
            self.__http.close()

    def __sign_request(
        self,
        url: str,
        headers: dict,
        signatures: typing.List[ActorKey],
        body: typing.Optional[typing.Union[dict, ActivityPubModel, bytes]] = None,
        sign_with: typing.List[
            typing.Literal["draft-cavage", "rsa2017", "fep8b32", "rfc9421"]
        ] = ["draft-cavage", "rsa2017", "fep8b32"],
    ) -> typing.Tuple[Optional[bytes], dict]:
        if isinstance(body, ActivityPubModel):
            body = body.to_json()

        signed_cavage = False
        signed_rsa2017 = False
        signed_fep8b32 = False
        signed_rfc9421 = False

        for signature in signatures:
            if isinstance(signature.private_key, rsa.RSAPrivateKey):
                if "rfc9421" in sign_with and not signed_rfc9421:
                    warnings.warn(
                        'This signature spec "rfc9421" is not implemented yet.',
                        category=NotImplementedWarning,
                        stacklevel=2,
                    )
                    signed_rfc9421 = True

                if "draft-cavage" in sign_with and not signed_cavage:
                    signer = draft.Signer(
                        headers=dict(headers) if headers else {},
                        method="POST",
                        url=str(url),
                        key_id=signature.key_id,
                        private_key=signature.private_key,
                        body=body if body else b"",
                    )
                    headers = signer.sign()
                    signed_cavage = True

                if "rsa2017" in sign_with and body and not signed_rsa2017:
                    ld_signer = apsig.LDSignature()
                    body = ld_signer.sign(
                        doc=(body if not isinstance(body, bytes) else json.loads(body)),
                        creator=signature.key_id,
                        private_key=signature.private_key,
                    )
                    signed_rsa2017 = True
            elif isinstance(signature.private_key, ed25519.Ed25519PrivateKey):
                if "fep8b32" in sign_with and body and not signed_fep8b32:
                    now = (
                        datetime.datetime.now().isoformat(sep="T", timespec="seconds")
                        + "Z"
                    )
                    fep_8b32_signer = apsig.ProofSigner(
                        private_key=signature.private_key
                    )
                    body = fep_8b32_signer.sign(
                        unsecured_document=(
                            body if not isinstance(body, bytes) else json.loads(body)
                        ),
                        options={
                            "type": "DataIntegrityProof",
                            "cryptosuite": "eddsa-jcs-2022",
                            "proofPurpose": "assertionMethod",
                            "verificationMethod": signature.key_id,
                            "created": now,
                        },
                    )
                    signed_fep8b32 = True
        if isinstance(body, bytes):
            return body, headers
        return json.dumps(body, ensure_ascii=False).encode("utf-8"), headers

    def __transform_to_bytes(
        self, content: typing.Union[bytes, str, dict, ActivityPubModel]
    ) -> bytes:
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode("utf-8")
        elif isinstance(content, dict):
            return json.dumps(content, ensure_ascii=False).encode("utf-8")
        elif isinstance(content, ActivityPubModel):
            return json.dumps(content.to_json(), ensure_ascii=False).encode("utf-8")

    def request(
        self,
        method: str,
        url: httpcore.URL | str,
        headers: dict = {},
        content: str | dict | ActivityPubModel | bytes | None = None,
        allow_redirect: bool = True,
        max_redirects: int = 5,
        signatures: typing.List[ActorKey] = [],
        sign_with: typing.List[
            typing.Literal["draft-cavage", "rsa2017", "fep8b32", "rfc9421"]
        ] = ["draft-cavage", "rsa2017", "fep8b32"],
    ) -> Response:
        if not self.__http:
            raise NotImplementedError
        if headers.get("user_agent") is None:
            headers["user_agent"] = self.user_agent
        if content is not None:
            content = self.__transform_to_bytes(content)
        if signatures != []:
            content, headers = sign_request(
                url=bytes(url).decode("ascii")
                if isinstance(url, httpcore.URL)
                else url,
                headers=headers,
                signatures=signatures,
                body=content,
                sign_with=sign_with,
                as_dict=False
            )
            if not isinstance(content, bytes):
                raise ValueError
        response = self.__http.request(
            method=method.upper(), url=url, headers=headers, content=content
        )
        if allow_redirect:
            if response.status in [301, 307, 308]:
                for i in range(max_redirects):
                    location = (
                        {
                            key.decode("utf-8"): value.decode("utf-8")
                            for key, value in response.headers
                        }
                    ).get("Location")
                    response = self.__http.request(
                        method=method.upper(),
                        url=location,
                        headers=headers,
                        content=content,
                    )
                    if response.status not in [301, 307, 308]:
                        return Response(response)
                raise TooManyRedirects
        return Response(response)

    def post(
        self,
        url: httpcore.URL | str,
        headers: dict = {},
        body: dict | str | bytes | None = None,
        allow_redirect: bool = True,
        max_redirects: int = 5,
        signatures: typing.List[ActorKey] = [],
        sign_with: typing.List[
            typing.Literal["draft-cavage", "rsa2017", "fep8b32", "rfc9421"]
        ] = ["draft-cavage", "rsa2017", "fep8b32"],
    ) -> Response:
        if body is not None:
            body = self.__transform_to_bytes(body)
        resp = self.request(
            "POST",
            url=url,
            headers=headers,
            content=body,
            allow_redirect=allow_redirect,
            max_redirects=max_redirects,
            signatures=signatures,
            sign_with=sign_with,
        )
        return resp

    def get(
        self,
        url: httpcore.URL | str,
        headers: dict = {},
        allow_redirect: bool = True,
        max_redirects: int = 5,
        signatures: typing.List[ActorKey] = [],
        sign_with: typing.List[
            typing.Literal["draft-cavage", "rsa2017", "fep8b32", "rfc9421"]
        ] = ["draft-cavage", "rsa2017", "fep8b32"],
    ) -> Response:
        resp = self.request(
            "GET",
            url=url,
            headers=headers,
            allow_redirect=allow_redirect,
            max_redirects=max_redirects,
            signatures=signatures,
            sign_with=sign_with,
        )
        return resp
