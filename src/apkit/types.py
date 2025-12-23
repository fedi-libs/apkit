from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa


class Outbox:
    pass


@dataclass
class ActorKey:
    key_id: str
    private_key: rsa.RSAPrivateKey | ed25519.Ed25519PrivateKey
