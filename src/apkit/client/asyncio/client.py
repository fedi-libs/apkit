import asyncio
import datetime
import json
from ssl import SSLContext
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    Union,
)

import aiohttp
from aiohttp.abc import AbstractCookieJar
from aiohttp.client import _CharsetResolver
from aiohttp.helpers import _SENTINEL, sentinel
from aiohttp.http_writer import (
    HttpVersion as HttpVersion,
)
from aiohttp.http_writer import (
    HttpVersion10 as HttpVersion10,
)
from aiohttp.http_writer import (
    HttpVersion11 as HttpVersion11,
)
from aiohttp.http_writer import (
    StreamWriter as StreamWriter,
)
from aiohttp.typedefs import JSONEncoder, LooseCookies, LooseHeaders, StrOrURL
import apsig
from apsig import draft
from apmodel.types import ActivityPubModel
from yarl import URL, Query
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from .types import _RequestContextManager, ActivityPubClientResponse
from .actor import ActorFetcher


class ActivityPubClient(aiohttp.ClientSession):
    def __init__(
        self,
        base_url: Optional[StrOrURL] = None,
        *,
        connector: Optional[aiohttp.BaseConnector] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cookies: Optional[LooseCookies] = None,
        headers: Optional[LooseHeaders] = None,
        proxy: Optional[StrOrURL] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        skip_auto_headers: Optional[Iterable[str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
        json_serialize: JSONEncoder = json.dumps,
        request_class: Type[aiohttp.ClientRequest] = aiohttp.ClientRequest,
        response_class: Type[aiohttp.ClientResponse] = ActivityPubClientResponse,
        ws_response_class: Type[
            aiohttp.ClientWebSocketResponse
        ] = aiohttp.ClientWebSocketResponse,
        version: HttpVersion = aiohttp.http.HttpVersion11,
        cookie_jar: Optional[AbstractCookieJar] = None,
        connector_owner: bool = True,
        raise_for_status: Union[
            bool, Callable[[aiohttp.ClientResponse], Awaitable[None]]
        ] = False,
        read_timeout: Union[float, _SENTINEL] = sentinel,
        conn_timeout: Optional[float] = None,
        timeout: Union[object, aiohttp.ClientTimeout] = sentinel,
        auto_decompress: bool = True,
        trust_env: bool = False,
        requote_redirect_url: bool = True,
        trace_configs: Optional[List[aiohttp.TraceConfig]] = None,
        read_bufsize: int = 2**16,
        max_line_size: int = 8190,
        max_field_size: int = 8190,
        fallback_charset_resolver: _CharsetResolver = lambda r, b: "utf-8",
        middlewares: Sequence[aiohttp.ClientMiddlewareType] = (),
        ssl_shutdown_timeout: Union[_SENTINEL, None, float] = sentinel,
    ) -> None:
        self.actor: ActorFetcher = ActorFetcher(self)
        super().__init__(
            base_url,
            connector=connector,
            loop=loop,
            cookies=cookies,
            headers=headers,
            proxy=proxy,
            proxy_auth=proxy_auth,
            skip_auto_headers=skip_auto_headers,
            auth=auth,
            json_serialize=json_serialize,
            request_class=request_class,
            response_class=response_class,
            ws_response_class=ws_response_class,
            version=version,
            cookie_jar=cookie_jar,
            connector_owner=connector_owner,
            raise_for_status=raise_for_status,
            read_timeout=read_timeout,
            conn_timeout=conn_timeout,
            timeout=timeout,
            auto_decompress=auto_decompress,
            trust_env=trust_env,
            requote_redirect_url=requote_redirect_url,
            trace_configs=trace_configs,
            read_bufsize=read_bufsize,
            max_line_size=max_line_size,
            max_field_size=max_field_size,
            fallback_charset_resolver=fallback_charset_resolver,
            middlewares=middlewares,
            ssl_shutdown_timeout=ssl_shutdown_timeout,
        )

    async def __aenter__(self) -> "ActivityPubClient":
        return self

    async def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        *,
        params: Query = None,
        data: Any = None,
        json: Any = None,
        cookies: Optional[LooseCookies] = None,
        headers: Optional[LooseHeaders] = None,
        skip_auto_headers: Optional[Iterable[str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
        allow_redirects: bool = True,
        max_redirects: int = 10,
        compress: Union[str, bool, None] = None,
        chunked: Optional[bool] = None,
        expect100: bool = False,
        raise_for_status: Union[
            None, bool, Callable[[aiohttp.ClientResponse], Awaitable[None]]
        ] = None,
        read_until_eof: bool = True,
        proxy: Optional[StrOrURL] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        timeout: Union[aiohttp.ClientTimeout, _SENTINEL] = sentinel,
        verify_ssl: Optional[bool] = None,
        fingerprint: Optional[bytes] = None,
        ssl_context: Optional[SSLContext] = None,
        ssl: Union[SSLContext, bool, aiohttp.Fingerprint] = True,
        server_hostname: Optional[str] = None,
        proxy_headers: Optional[LooseHeaders] = None,
        trace_request_ctx: Optional[Mapping[str, Any]] = None,
        read_bufsize: Optional[int] = None,
        auto_decompress: Optional[bool] = None,
        max_line_size: Optional[int] = None,
        max_field_size: Optional[int] = None,
        middlewares: Optional[Sequence[aiohttp.ClientMiddlewareType]] = None,
    ) -> ActivityPubClientResponse:
        return await super()._request(
            method,
            str_or_url,
            params=params,
            data=data,
            json=json,
            cookies=cookies,
            headers=headers,
            skip_auto_headers=skip_auto_headers,
            auth=auth,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            compress=compress,
            chunked=chunked,
            expect100=expect100,
            raise_for_status=raise_for_status,
            read_until_eof=read_until_eof,
            proxy=proxy,
            proxy_auth=proxy_auth,
            timeout=timeout,
            verify_ssl=verify_ssl,
            fingerprint=fingerprint,
            ssl_context=ssl_context,
            ssl=ssl,
            server_hostname=server_hostname,
            proxy_headers=proxy_headers,
            trace_request_ctx=trace_request_ctx,
            read_bufsize=read_bufsize,
            auto_decompress=auto_decompress,
            max_line_size=max_line_size,
            max_field_size=max_field_size,
            middlewares=middlewares,
        )  # pyright: ignore[reportArgumentType, reportReturnType]

    def get( # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        url: str | URL,
        *,
        allow_redirects: bool = True,
        headers: Optional[LooseHeaders] = None,
        key_id: Optional[str] = None,
        signature: Optional[Union[rsa.RSAPrivateKey, ed25519.Ed25519PrivateKey]] = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        return _RequestContextManager(
            self._request(
                aiohttp.hdrs.METH_GET,
                url,
                allow_redirects=allow_redirects,
                headers=headers,
                **kwargs,
            )
        )

    def post(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        url: str | URL,
        *,
        key_id: str,
        signature: Union[rsa.RSAPrivateKey, ed25519.Ed25519PrivateKey],
        sign_http: bool = True,
        sign_ld: bool = False,
        json: Union[dict, ActivityPubModel] = {},
        headers: Optional[LooseHeaders] = None,
        **kwargs: Any,
    ) -> _RequestContextManager:
        if isinstance(json, ActivityPubModel):
            json = json.to_json()
        if not isinstance(signature, ed25519.Ed25519PrivateKey):
            if sign_http:
                signer = draft.Signer(
                    headers=dict(headers) if headers else {},
                    method="POST",
                    url=str(url),
                    key_id=key_id,
                    private_key=signature,
                    body=json,
                )
                headers = signer.sign()

            if sign_ld:
                ld_signer = apsig.LDSignature()
                json = ld_signer.sign(doc=json, creator=key_id, private_key=signature)
        else:
            if sign_http:
                now = (
                    datetime.datetime.now().isoformat(sep="T", timespec="seconds") + "Z"
                )
                fep_8b32_signer = apsig.ProofSigner(private_key=signature)
                json = fep_8b32_signer.sign(
                    unsecured_document=json,
                    options={
                        "type": "DataIntegrityProof",
                        "cryptosuite": "eddsa-jcs-2022",
                        "proofPurpose": "assertionMethod",
                        "verificationMethod": key_id,
                        "created": now,
                    },
                )
        return _RequestContextManager(
            self._request(aiohttp.hdrs.METH_POST, url, json=json, headers=headers, **kwargs)
        )
