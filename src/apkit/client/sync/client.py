import datetime
import json
import typing
import warnings

import apsig
import httpcore
from apmodel.types import ActivityPubModel
from apsig import draft
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from typing_extensions import Optional

from ..._version import __version__
from ...types import ActorKey
from .._common import ensure_user_agent_and_reconstruct, sign_request
from .actor import ActorFetcher
from .exceptions import TooManyRedirects
from .types import Response


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
            return json.dumps(content.to_json(), ensure_ascii=False).encode(
                "utf-8"
            )

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
        headers = ensure_user_agent_and_reconstruct(headers, self.user_agent)
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
                as_dict=False,
            )
            if not isinstance(content, bytes):
                raise ValueError
        response = self.__http.request(
            method=method.upper(), url=url, headers=headers, content=content
        )
        if allow_redirect:
            if response.status in [301, 307, 308]:
                for _ in range(max_redirects):
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
