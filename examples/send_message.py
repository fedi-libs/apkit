import asyncio
import logging
import os
import uuid
import sys

from apkit.client.asyncio import ActivityPubClient
from apkit.models import Person, Note, CryptographicKey, Create
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization
from datetime import datetime, UTC
from apkit.client.models import Resource as WebfingerResource

if len(sys.argv) < 2:
    print("USAGE: python send_message.py <RECEPIENT_URI>", file=sys.stderr)
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


async def send_note(recepient: str) -> None:
    async with ActivityPubClient() as client:
        if not recepient.startswith("http"):
            # this a human readable account name like alice@example.net

            # remove a possible @ sign at the start
            recepient = recepient.lstrip("@")

            # Use Webfinger to find the actor's URI
            res = WebfingerResource.parse(recepient)
            webfinger_result = await client.actor.resolve(res.username, res.host)

            # read the ActivityPub link from the result
            recepient = webfinger_result.get("application/activity+json").href

        # Fetch a remote Actor
        target_actor = await client.actor.fetch(recepient)
        logger.info(f"Fetched actor: {target_actor.name}")

        # Get the inbox URL from the actor's profile
        inbox_url = target_actor.inbox
        if not inbox_url:
            raise Exception("Could not find actor's inbox URL")

        logger.info(f"Found actor's inbox: {inbox_url}")

        # Create note
        note = Note(
            id=f"https://{HOST}/notes/{uuid.uuid4()}",
            attributedTo=actor.id,
            content="<p>Hello from apkit</p>",
            published=datetime.now(UTC).isoformat() + "Z",
            to=[target_actor.id],
            cc=["https://www.w3.org/ns/activitystreams#Public"],
        )

        # Create activity
        create = Create(
            id=f"https://{HOST}/creates/{uuid.uuid4()}",
            actor=actor.id,
            object=note,
            published=datetime.now(UTC).isoformat() + "Z",
            to=note.to,
            cc=note.cc,
        )

        # Deliver the activity
        logger.info("Delivering activity...")

        # Uncomment the following line if you want to see the code of the activity.
        # print(create.to_json())

        resp = await client.post(
            inbox_url,
            key_id=actor.publicKey.id,
            signature=private_key,
            json=create.to_json(keep_object=True),
        )
        logger.info(f"Delivery result: {resp.status}")

        if resp.status >= 200 and resp.status <= 299:
            logger.info(f"Note id: {note.id}")


if __name__ == "__main__":
    recepient = sys.argv[1]

    asyncio.run(send_note(recepient))
