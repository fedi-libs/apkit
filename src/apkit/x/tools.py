from apmodel import Actor, Multikey
from apmodel.security.cryptographickey import CryptographicKey

async def get_keys(actor: Actor):
    keys = {}
    if isinstance(actor.publicKey, CryptographicKey):
        keys[actor.publicKey.id] = actor.publicKey.publicKeyPem
    if actor.assertionMethod:
        for method in actor.assertionMethod:
            if isinstance(method, Multikey):
                keys[method.id] = method.publicKeyMultibase
    return keys