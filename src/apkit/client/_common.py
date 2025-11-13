# This file will contain common logic shared between sync and asyncio clients.
import datetime
import json
import warnings
from typing import (
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    Union,
)

import apsig
from aiohttp.typedefs import LooseHeaders
from apmodel.types import ActivityPubModel
from apsig import draft
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from ..types import ActorKey
from .exceptions import NotImplementedWarning
from .models import Resource, WebfingerResult


def ensure_user_agent_and_reconstruct(
    headers: LooseHeaders, user_agent: str
) -> Dict[str, str]:
    processed_headers: Dict[str, str] = {}

    if isinstance(headers, Mapping):
        for k, v in headers.items():
            key_str = str(k)
            key_lower = key_str.lower()

            if key_lower not in processed_headers:
                processed_headers[key_lower] = v
                processed_headers[key_lower + "_original_key"] = key_str

    elif isinstance(headers, Iterable):
        for k, v in headers:
            key_str = str(k)
            key_lower = key_str.lower()

            if key_lower not in processed_headers:
                processed_headers[key_lower] = v
                processed_headers[key_lower + "_original_key"] = key_str

    else:
        raise TypeError(f"Unsupported header type: {type(headers)}")

    user_agent_key_lower = "user-agent"
    if user_agent_key_lower not in processed_headers:
        processed_headers[user_agent_key_lower] = user_agent
        processed_headers[user_agent_key_lower + "_original_key"] = "User-Agent"

    final_headers: Dict[str, str] = {}
    for key_lower, value in processed_headers.items():
        if key_lower.endswith("_original_key"):
            continue

        original_key = processed_headers.get(key_lower + "_original_key")

        if original_key:
            final_headers[original_key] = value
        else:
            standard_key = key_lower.replace("-", " ").title().replace(" ", "-")
            final_headers[standard_key] = value

    return final_headers


def sign_request(
    url: str,
    headers: dict,
    signatures: List[ActorKey],
    body: Optional[Union[dict, ActivityPubModel, bytes]] = None,
    sign_with: List[
        Literal["draft-cavage", "rsa2017", "fep8b32", "rfc9421"]
    ] = [
        "draft-cavage",
        #        "rsa2017",
        #        "fep8b32",
    ],
    as_dict: bool = False,
) -> Tuple[Optional[Union[bytes, dict]], dict]:
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
                    doc=(
                        body
                        if not isinstance(body, bytes)
                        else json.loads(body)
                    ),
                    creator=signature.key_id,
                    private_key=signature.private_key,
                )
                signed_rsa2017 = True
        elif isinstance(signature.private_key, ed25519.Ed25519PrivateKey):
            if "fep8b32" in sign_with and body and not signed_fep8b32:
                now = (
                    datetime.datetime.now().isoformat(
                        sep="T", timespec="seconds"
                    )
                    + "Z"
                )
                fep_8b32_signer = apsig.ProofSigner(
                    private_key=signature.private_key
                )
                body = fep_8b32_signer.sign(
                    unsecured_document=(
                        body
                        if not isinstance(body, bytes)
                        else json.loads(body)
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


def _is_expected_content_type(
    actual_ctype: str, expected_ctype_prefix: str
) -> bool:
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
