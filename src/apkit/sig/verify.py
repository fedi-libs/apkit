import json
from typing import Optional, Union

from apsig import draftVerifier
from apsig import LDSignature
from apsig import ProofVerifier
from apsig.exceptions import SignatureError

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives import serialization

class Verifier:
    def __init__(self, public_key_ed: Optional[Union[str, ed25519.Ed25519PublicKey]] = None) -> None:
        if public_key_ed:
            self.proof = ProofVerifier(public_key_ed)
        else:
            self.proof = None
        self.ld = LDSignature()
        self.draft = draftVerifier()

    def verify(self, document: dict, public_key: rsa.RSAPublicKey, method: str, url: str, headers: dict):
        body = json.dumps(document, ensure_ascii=False).encode("utf-8")
        if self.proof:
            proof = self.proof.verify_proof(document)
            if proof.get("verified"):
                return True
        try:
            self.ld.verify(document, public_key)
            return True
        except SignatureError:
            draft, _ = self.draft.verify(public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo), method, url, headers, body) # type: ignore
            if draft:
                return True
            return False