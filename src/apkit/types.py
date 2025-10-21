from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

class Outbox:
    pass

@dataclass
class ActorKey:
    key_id: str
    private_key: rsa.RSAPrivateKey | ed25519.Ed25519PrivateKey
