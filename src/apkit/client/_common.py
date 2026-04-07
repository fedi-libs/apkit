import datetime
import json
import urllib.parse
import warnings
from collections.abc import Iterable, Mapping
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import apmodel
import apsig
from apmodel.types import ActivityPubModel
from apsig import draft
from apsig.rfc9421 import RFC9421Signer
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from typing_extensions import ParamSpec

from apkit.types import ActorKey

from .models import Resource, WebfingerResult

P = ParamSpec("P")
R = TypeVar("R")


def reconstruct_headers(
    headers: Any,
    user_agent: str,
    json: Optional[dict | ActivityPubModel | Any] = None,
) -> Dict[str, str]:
    final_headers: Dict[str, str] = {}
    key_map: Dict[str, str] = {}

    match headers:
        case Mapping() as m:
            items = m.items()
        case Iterable() as i:
            items = i
        case None:
            items = []
        case _:
            raise TypeError(f"Unsupported header type: {type(headers)}")

    for k, v in items:
        k_str = str(k)
        k_lower = k_str.lower()
        if k_lower not in key_map:
            key_map[k_lower] = k_str
            final_headers[k_str] = str(v)

    if "user-agent" not in key_map:
        final_headers["User-Agent"] = user_agent
        key_map["user-agent"] = "User-Agent"

    if json and "content-type" not in key_map:
        match json:
            case ActivityPubModel():
                final_headers["Content-Type"] = (
                    "application/activity+json; charset=UTF-8"
                )
            case dict():
                final_headers["Content-Type"] = "application/json"

    return final_headers


def build_webfinger_url(host: str, resource: Resource) -> str:
    """Builds a WebFinger URL."""
    return f"https://{host}/.well-known/webfinger?resource={resource}"


def validate_webfinger_result(
    result: WebfingerResult, expected_subject: Resource
) -> None:
    """Validates the subject in a WebfingerResult."""
    if result.subject != expected_subject:
        raise ValueError(
            f"Mismatched subject in response. Expected {expected_subject}, got {result.subject}"
        )


def _is_expected_content_type(actual_ctype: str, expected_ctype_prefix: str) -> bool:
    mime_type = actual_ctype.split(";")[0].strip().lower()

    if mime_type == "application/json":
        return True
    if mime_type.endswith("+json"):
        return True

    if expected_ctype_prefix and mime_type.startswith(
        expected_ctype_prefix.split(";")[0].lower()
    ):
        return True

    return False


def sign_request(
    url: str,
    headers: dict,
    signatures: List[ActorKey],
    body: Optional[Union[dict, ActivityPubModel, bytes]] = None,
    sign_with: List[str] = [
        "draft-cavage",
        #        "rsa2017",
        #        "fep8b32",
    ],
    as_dict: bool = False,
) -> Tuple[Optional[bytes | dict], dict]:
    if isinstance(body, ActivityPubModel):
        body = apmodel.to_dict(body)

    signed_cavage = False
    signed_rsa2017 = False
    signed_fep8b32 = False
    signed_rfc9421 = False

    for signature in signatures:
        if isinstance(signature.private_key, RSAPrivateKey):
            if "rfc9421" in sign_with and not signed_rfc9421:
                if "draft-cavage" in sign_with:
                    warnings.warn(
                        "Draft and RFC9421 Signing is exclusive. "
                        "Legacy Draft mode is enabled to maintain compatibility. "
                        "The RFC 9421 (Structured Fields) signing logic will not be applied to this message.",
                        UserWarning,
                    )
                    signed_rfc9421 = True
                else:
                    parsed_url = urllib.parse.urlparse(url)
                    if parsed_url.hostname:
                        rfc_signer = RFC9421Signer(
                            signature.private_key, signature.key_id
                        )
                        headers = rfc_signer.sign(
                            headers=dict(headers) if headers else {},
                            method="POST",
                            host=parsed_url.hostname,
                            path=parsed_url.path,
                            body=body if body else b"",
                        )
                    signed_rfc9421 = True

            if "draft-cavage" in sign_with and not signed_cavage:
                if "rfc9421" in sign_with:
                    warnings.warn(
                        "Draft and RFC9421 Signing is exclusive. "
                        "Legacy Draft mode is enabled to maintain compatibility. "
                        "The RFC 9421 (Structured Fields) signing logic will not be applied to this message.",
                        UserWarning,
                    )
                    signed_rfc9421 = True
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
        elif isinstance(signature.private_key, Ed25519PrivateKey):
            if "fep8b32" in sign_with and body and not signed_fep8b32:
                now = (
                    datetime.datetime.now().isoformat(sep="T", timespec="seconds") + "Z"
                )
                fep_8b32_signer = apsig.ProofSigner(private_key=signature.private_key)
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
    if not as_dict:
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    return body, headers


def delegate_target(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper
