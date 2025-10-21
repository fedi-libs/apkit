# Using the Client

The `apkit.client` module provides clients for communicating with other ActivityPub servers. There are two types of clients available:

- **Asynchronous Client (`apkit.client.asyncio`):** This client is based on `aiohttp` and is suitable for applications that require non-blocking I/O operations. It's the recommended choice for web servers and other high-concurrency applications.
- **Synchronous Client (`apkit.client.sync`):** This client is based on `httpcore` (the foundation of `httpx`) and provides a blocking, synchronous interface. It's easier to use in scripts or applications that don't require the complexity of `asyncio`.

The choice between the two depends on your application's architecture. The asynchronous client offers better performance for I/O-bound tasks, while the synchronous client is simpler to integrate into traditional, linear programs.

This is a very simple example:

=== "Asynchronous"

    ```python
    import asyncio
    from apkit.client.asyncio import ActivityPubClient

    async def main():
        async with ActivityPubClient() as client:
            # Fetch a remote Actor or Object
            actor = await client.actor.fetch("https://example.com/users/someuser")
            if actor:
                print(f"Fetched actor: {actor.name}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "Synchronous"

    ```python
    from apkit.client.sync import ActivityPubClient

    def main():
        with ActivityPubClient() as client:
            # Fetch a remote Actor or Object
            actor = client.actor.fetch("https://example.com/users/someuser")
            if actor:
                print(f"Fetched actor: {actor.name}")

    if __name__ == "__main__":
        main()
    ```

When sending activities to another server, this server usually wants to verify the signature.
This requires some interaction. Therefore, it is easiest to start the minimal server from the [tutorial](../tutorial).
It will take care to answer the WebFinger requests, send the required `application/activity+json` documents and public key.

## Create a Note

This is a simple example to send a _Note_ to another ActivityPub server.
First, some preparations need to be made, which must be done only once before all activities.

1. The programs loads or creates a private key required to sign activities.
2. A _Person_ resource is created that will be used as the _Actor_ of activities.

The function `send_note` contains the code to create a _Note_.

1. Find the address of the receiver's inbox.
2. Create a _Note_ object.
3. Create a _Create_ activity that contains the _Note_.
4. Deliver the _Create_ activity to the receiver's inbox.

=== "Asynchronous"

    ```python
    import asyncio
    import logging
    import os
    import uuid

    from apkit.client.asyncio import ActivityPubClient
    from apkit.models import Person, Note, CryptographicKey, Create, Delete
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from datetime import datetime, UTC

    HOST="social.example.com"      # <<< Change this to your domain name
    USER_ID="demo"
    TARGET_ID="https://example.org/users/alice"   # <<< Change this to the URI of the account you want to send something to

    # --- Logging Setup ---
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # --- Key Persistence ---
    KEY_FILE = "private_key.pem"

    if os.path.exists(KEY_FILE):
        logger.info(f"Loading existing private key from {KEY_FILE}.")
        with open(KEY_FILE, "rb") as f:
            private_key = crypto_serialization.load_pem_private_key(f.read(), password=None)
    else:
        logger.info(f"No key file found. Generating new private key and saving to {KEY_FILE}.")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PrivateFormat.PKCS8,
                encryption_algorithm=crypto_serialization.NoEncryption()
            ))

    public_key_pem = private_key.public_key().public_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # --- Create actor ---
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
            publicKeyPem=public_key_pem
        )
    )

    async def send_note():
        async with ActivityPubClient() as client:
            # Fetch a remote Actor
            target_actor = await client.actor.fetch(TARGET_ID)
            print(f"Fetched actor: {target_actor.name}")

            # Get the inbox URL from the actor's profile
            inbox_url = target_actor.inbox
            if not inbox_url:
                raise Exception("Could not find actor's inbox URL")

            logger.info(f"Found actor's inbox: {inbox_url}")

            # --- Create note ---
            note = Note(
                id=f"https://{HOST}/notes/{uuid.uuid4()}",
                attributedTo=actor.id,
                content=f"<p>Hello from apkit</p>",
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=[target_actor.id],
                cc=["https://www.w3.org/ns/activitystreams#Public"],
            )

            # --- Create activity ---
            create = Create(
                id=f"https://{HOST}/creates/{uuid.uuid4()}",
                actor=actor.id,
                object=note.to_json(),            # embed the note into the activity
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=note.to,                       # re-use the information from the note
                cc=note.cc
            )

            # Deliver the activity
            logger.info("Delivering activity...")

            # If you are interested in the actual data, uncomment this line.
            # print(create.to_json())

            resp = await client.post(
                inbox_url,                  # address of the receiver's inbox
                key_id=actor.publicKey.id,  # the id of our public key
                signature=private_key,      # this is our private key
                json=create                 # the activity to send
            )
            logger.info(f"Delivery result: {resp.status}")
            logger.info(f"Note id: {note.id}")

    if __name__ == "__main__":
        asyncio.run(send_note())
    ```

=== "Synchronous"

    ```python
    import logging
    import os
    import uuid

    from apkit.client.sync import ActivityPubClient
    from apkit.models import Person, Note, CryptographicKey, Create, Delete
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from datetime import datetime, UTC

    HOST="social.example.com"      # <<< Change this to your domain name
    USER_ID="demo"
    TARGET_ID="https://example.org/users/alice"   # <<< Change this to the URI of the account you want to send something to

    # --- Logging Setup ---
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # --- Key Persistence ---
    KEY_FILE = "private_key.pem"

    if os.path.exists(KEY_FILE):
        logger.info(f"Loading existing private key from {KEY_FILE}.")
        with open(KEY_FILE, "rb") as f:
            private_key = crypto_serialization.load_pem_private_key(f.read(), password=None)
    else:
        logger.info(f"No key file found. Generating new private key and saving to {KEY_FILE}.")
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PrivateFormat.PKCS8,
                encryption_algorithm=crypto_serialization.NoEncryption()
            ))

    public_key_pem = private_key.public_key().public_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # --- Create actor ---
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
            publicKeyPem=public_key_pem
        )
    )

    def send_note():
        with ActivityPubClient() as client:
            # Fetch a remote Actor
            target_actor = client.actor.fetch(TARGET_ID)
            print(f"Fetched actor: {target_actor.name}")

            # Get the inbox URL from the actor's profile
            inbox_url = target_actor.inbox
            if not inbox_url:
                raise Exception("Could not find actor's inbox URL")

            logger.info(f"Found actor's inbox: {inbox_url}")

            # --- Create note ---
            note = Note(
                id=f"https://{HOST}/notes/{uuid.uuid4()}",
                attributedTo=actor.id,
                content=f"<p>Hello from apkit</p>",
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=[target_actor.id],
                cc=["https://www.w3.org/ns/activitystreams#Public"],
            )

            # --- Create activity ---
            create = Create(
                id=f"https://{HOST}/creates/{uuid.uuid4()}",
                actor=actor.id,
                object=note.to_json(),            # embed the note into the activity
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=note.to,                       # re-use the information from the note
                cc=note.cc
            )

            # Deliver the activity
            logger.info("Delivering activity...")

            # If you are interested in the actual data, uncomment this line.
            # print(create.to_json())

            resp = client.post(
                inbox_url,                  # address of the receiver's inbox
                key_id=actor.publicKey.id,  # the id of our public key
                signature=private_key,      # this is our private key
                json=create                 # the activity to send
            )
            logger.info(f"Delivery result: {resp.status}")
            logger.info(f"Note id: {note.id}")

    if __name__ == "__main__":
        send_note()
    ```

In a productiv environment you will want to store the content of the note and its URI into some kind of persistent storage.
Then, for example, likes could be correctly assigned.

## Delete something

The last information the function to create a _Note_ writes on the terminal is the URI by which the
_Note_ can be identified. It can also be used to remove it from another ActivityPub server.
Here is some demo code for that:

=== "Asynchronous"

    ```python
    async def delete_note():

        URI = "https://social.example.com/notes/6de49020-85a0-4546-b63e-36fe23271f71"   # <<< change this URI

        async with ActivityPubClient() as client:
            # Fetch a remote Actor
            target_actor = await client.actor.fetch(TARGET_ID)
            print(f"Fetched actor: {target_actor.name}")

            # Get the inbox URL from the actor's profile
            inbox_url = target_actor.inbox
            if not inbox_url:
                raise Exception("Could not find actor's inbox URL")

            logger.info(f"Found actor's inbox: {inbox_url}")

            # Delete activity
            delete = Delete(
                id=f"https://{HOST}/activities/{uuid.uuid4()}",
                actor=actor.id,
                object=URI,
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=[target_actor.id],
                cc=["https://www.w3.org/ns/activitystreams#Public"],
            )

            # Deliver the activity
            logger.info("Delivering activity...")

            resp = await client.post(
                inbox_url,
                key_id=actor.publicKey.id,
                signature=private_key,
                json=delete
            )
            logger.info(f"Delivery result: {resp.status}")
    ```

=== "Synchronous"

    ```python
    def delete_note():

        URI = "https://social.example.com/notes/6de49020-85a0-4546-b63e-36fe23271f71"   # <<< change this URI

        with ActivityPubClient() as client:
            # Fetch a remote Actor
            target_actor = client.actor.fetch(TARGET_ID)
            print(f"Fetched actor: {target_actor.name}")

            # Get the inbox URL from the actor's profile
            inbox_url = target_actor.inbox
            if not inbox_url:
                raise Exception("Could not find actor's inbox URL")

            logger.info(f"Found actor's inbox: {inbox_url}")

            # Delete activity
            delete = Delete(
                id=f"https://{HOST}/activities/{uuid.uuid4()}",
                actor=actor.id,
                object=URI,
                published=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                to=[target_actor.id],
                cc=["https://www.w3.org/ns/activitystreams#Public"],
            )

            # Deliver the activity
            logger.info("Delivering activity...")

            resp = client.post(
                inbox_url,
                key_id=actor.publicKey.id,
                signature=private_key,
                json=delete
            )
            logger.info(f"Delivery result: {resp.status}")
    ```