import asyncio
import logging
import os
import uuid
import sys

from apkit.client.asyncio import ActivityPubClient
from apkit.models import Person, CryptographicKey, Delete
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization
from datetime import datetime, UTC

if len(sys.argv) < 3:
    print("USAGE: python delete.py <RECEPIENT_URI> <OBJECT_ID>", file=sys.stderr)
    sys.exit(1)


# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
HOST = os.getenv("APKIT_DOMAIN")
if HOST is None:
    logger.error(
        "Envirconment variable APKIT_DOMAIN is not set. See README.md how to set the variable."
    )
    sys.exit(1)

logger.info(f"Using {HOST} as host name.")

USER_ID = "demo"

# --- Key Persistence ---
KEY_FILE = "private_key.pem"

if os.path.exists(KEY_FILE):
    logger.info(f"Loading existing private key from {KEY_FILE}.")
    with open(KEY_FILE, "rb") as f:
        private_key = crypto_serialization.load_pem_private_key(f.read(), password=None)
else:
    logger.info(
        f"No key file found. Generating new private key and saving to {KEY_FILE}."
    )
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(KEY_FILE, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PrivateFormat.PKCS8,
                encryption_algorithm=crypto_serialization.NoEncryption(),
            )
        )

public_key_pem = (
    private_key.public_key()
    .public_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode("utf-8")
)

# Create actor
actor = Person(
    id=f"https://{HOST}/users/{USER_ID}",
    name="apkit Demo",
    preferredUsername="demo",
    summary="This is a demo actor powered by apkit!",
    inbox=f"https://{HOST}/users/{USER_ID}/inbox",
    outbox=f"https://{HOST}/users/{USER_ID}/outbox",
    publicKey=CryptographicKey(
        id=f"https://{HOST}/users/{USER_ID}#main-key",
        owner=f"https://{HOST}/users/{USER_ID}",
        publicKeyPem=public_key_pem,
    ),
)


async def delete_note(recepient: str, object_id: str) -> None:
    async with ActivityPubClient() as client:
        # Fetch a remote Actor
        target_actor = await client.actor.fetch(recepient)
        logger.info(f"Fetched actor: {target_actor.name}")

        # Get the inbox URL from the actor's profile
        inbox_url = target_actor.inbox
        if not inbox_url:
            raise Exception("Could not find actor's inbox URL")

        logger.info(f"Found actor's inbox: {inbox_url}")

        # Delete activity
        delete = Delete(
            id=f"https://{HOST}/activities/{uuid.uuid4()}",
            actor=f"https://{HOST}/users/{USER_ID}",
            object=object_id,
            published=datetime.now(UTC).isoformat() + "Z",
            to=[target_actor.id],
            cc=["https://www.w3.org/ns/activitystreams#Public"],
        )

        # Deliver the activity
        logger.info("Delivering activity...")

        resp = await client.post(
            inbox_url, key_id=actor.publicKey.id, signature=private_key, json=delete
        )
        logger.info(f"Delivery result: {resp.status}")


if __name__ == "__main__":
    recepient = sys.argv[1]
    object_id = sys.argv[2]

    asyncio.run(delete_note(recepient, object_id))
