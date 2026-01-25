from cryptography.hazmat.primitives.asymmetric import rsa
from apkit.config import AppConfig
from apkit.helper.inbox import InboxVerifier
from apsig import draft, ld_signature
from apkit.models import CryptographicKey, Person
from cryptography.hazmat.primitives import serialization as crypto_serialization

import json
import pytest


def _prepare_signed_request():
    # prepare private and public keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )

    # create an activity with an embedded Actor
    body_json = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "https://example.com/likes",
        "type": "Like",
        "actor": {
            "id": "https://example.com/actor",
            "type": "Person",
            "publicKey": {
                "id": "http://example.com/actor#key",
                "owner": "https://example.com/actor",
                "publicKeyPem": public_key_pem,
            },
        },
        "object": "https://example.com/5",
    }

    body = json.dumps(body_json).encode("utf-8")

    url = "http://example.com/ap"
    method = "POST"
    headers = {"host": "example.com"}

    # sign the request
    signer = draft.Signer(
        headers=headers,
        method=method,
        url=url,
        key_id="http://example.com/actor#key",
        private_key=private_key,
        body=body,
    )
    headers = signer.sign()

    # the verifier expects all HTTP header names in lower case
    headers["signature"] = headers["Signature"]

    return (body, url, method, headers)


@pytest.mark.asyncio
async def test_verify_draft_http_signature():
    (body, url, method, headers) = _prepare_signed_request()

    config = AppConfig()
    inbox_verifier = InboxVerifier(config)

    result = await inbox_verifier.verify(body, url, method, headers)
    assert result == True
