# Getting Started with apkit

This tutorial will guide you through creating a basic ActivityPub server using `apkit`. You'll learn how to create an actor, make it discoverable, and handle incoming `Follow` requests.

## Prerequisites

`apkit`'s server module is built on FastAPI. To get started, you'll need to install `apkit` with the `server` extras.

```bash
pip install "apkit[server]"
```

You will also need an ASGI server to run your application. We'll use `uvicorn` in this tutorial.

```bash
pip install uvicorn
```

## 1. Basic Server and Actor Setup

First, let's import the necessary components and set up a basic server and a `Person` actor.

```python
# main.py
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization

from apkit.server import ActivityPubServer, SubRouter
from apkit.server.types import Context, ActorKey
from apkit.server.responses import ActivityResponse
from apkit.models import (
    Person, CryptographicKey, Follow, Actor as APKitActor,
    Nodeinfo, NodeinfoSoftware, NodeinfoProtocol, NodeinfoServices, NodeinfoUsage, NodeinfoUsageUsers
)
from apkit.client import WebfingerResource, WebfingerResult, WebfingerLink
from apkit.client.asyncio.client import ActivityPubClient

# --- Configuration ---
HOST = "example.com"
USER_ID = str(uuid.uuid4())

# --- Key Generation (for demonstration) ---
# In a real application, you would load a persistent key from a secure storage.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key_pem = private_key.public_key().public_bytes(
    encoding=crypto_serialization.Encoding.PEM,
    format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# --- Actor Definition ---
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

# --- Server Initialization ---
app = ActivityPubServer()
```

## 2. Serving the Actor

To make your actor accessible to others, you need an endpoint that serves the actor object.

```python
# main.py (continued)
@app.get("/users/{identifier}")
async def get_actor_endpoint(identifier: str):
    if identifier == USER_ID:
        return ActivityResponse(actor)
    return JSONResponse({"error": "Not Found"}, status_code=404)
```

## 3. Making the Actor Discoverable with Webfinger

Webfinger allows users on other servers to find your actor using an address like `demo@example.com`.

```python
# main.py (continued)
@app.webfinger()
async def webfinger_endpoint(request: Request, acct: WebfingerResource) -> Response:
    if acct.username == "demo" and acct.host == HOST:
        link = WebfingerLink(
            rel="self",
            type="application/activity+json",
            href=f"https://{HOST}/users/{USER_ID}"
        )
        wf_result = WebfingerResult(subject=acct, links=[link])
        return JSONResponse(wf_result.to_json(), media_type="application/jrd+json")
    return JSONResponse({"message": "Not Found"}, status_code=404)
```

## 4. Setting up the Inbox

Before your server can receive activities, you need to define an inbox endpoint. The `app.inbox()` method registers a URL pattern as an inbox. Any valid POST request to this URL will be processed by your activity handlers.

```python
# main.py (continued)
app.inbox("/users/{identifier}/inbox")
```

## 5. Handling Incoming Activities

The `@app.on()` decorator registers a handler for specific incoming activities. Let's create a handler for `Follow` requests that automatically sends back a signed `Accept` activity.

```python
# main.py (continued)

# This function provides the private key for signing outgoing activities.
async def get_keys_for_actor(identifier: str) -> list[ActorKey]:
    if identifier == USER_ID:
        return [ActorKey(key_id=actor.publicKey.id, private_key=private_key)]
    return []

@app.on(Follow)
async def on_follow_activity(ctx: Context):
    activity = ctx.activity
    if not isinstance(activity, Follow):
        return JSONResponse({"error": "Invalid activity type"}, status_code=400)

    # Resolve the actor who sent the Follow request
    follower_actor = None
    if isinstance(activity.actor, str):
        async with ActivityPubClient() as client:
            follower_actor = await client.actor.fetch(activity.actor)
    elif isinstance(activity.actor, APKitActor):
        follower_actor = activity.actor

    if not follower_actor:
        return JSONResponse({"error": "Could not resolve follower actor"}, status_code=400)

    # Automatically accept the follow request
    accept_activity = activity.accept()

    # Send the signed Accept activity back to the follower's inbox
    await ctx.send(
        get_keys_for_actor,
        follower_actor,
        accept_activity
    )
    return Response(status_code=202)
```

## 6. Adding Server Metadata with NodeInfo

[NodeInfo](https://nodeinfo.diaspora.software/) is a protocol to publish standardized metadata about your server. `apkit` provides a simple decorator to expose this information.

```python
# main.py (continued)
@app.nodeinfo("/nodeinfo/2.1", "2.1")
async def nodeinfo_endpoint():
    return ActivityResponse(
        Nodeinfo(
            version="2.1",
            software=NodeinfoSoftware(name="apkit-demo", version="0.1.0"),
            protocols=[NodeinfoProtocol.ACTIVITYPUB],
            services=NodeinfoServices(inbound=[], outbound=[]),
            openRegistrations=False,
            usage=NodeinfoUsage(users=NodeinfoUsageUsers(total=1)),
            metadata={},
        )
    )
```

## 7. Organizing your code with SubRouter

For larger applications, you can use `SubRouter`, which works just like FastAPI's `APIRouter`. It allows you to organize your endpoints into different files. `SubRouter` also supports `apkit`-specific decorators like `@sub.nodeinfo()`.

```python
# main.py (continued)
# You could move this to a separate file, e.g., `nodeinfo.py`
sub = SubRouter()

@sub.nodeinfo("/ni/2.0", "2.0")
async def nodeinfo_20_endpoint():
    # ... (implementation similar to the above)
    pass

app.include_router(sub)
```

## 8. Running the Server

Save the complete code to a file named `main.py`. You can then run it with `uvicorn`.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Your simple ActivityPub server is now running! You can test it by searching for `@demo@example.com` from another Fediverse instance.

## 9. Full Code Example

Here is the complete code for `main.py`:

```python
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization

from apkit.server import ActivityPubServer, SubRouter
from apkit.server.types import Context, ActorKey
from apkit.server.responses import ActivityResponse
from apkit.models import (
    Person, CryptographicKey, Follow, Actor as APKitActor,
    Nodeinfo, NodeinfoSoftware, NodeinfoProtocol, NodeinfoServices, NodeinfoUsage, NodeinfoUsageUsers
)
from apkit.client import WebfingerResource, WebfingerResult, WebfingerLink
from apkit.client.asyncio.client import ActivityPubClient

# --- Configuration ---
HOST = "example.com"
USER_ID = str(uuid.uuid4())

# --- Key Generation (for demonstration) ---
# In a real application, you would load a persistent key from a secure storage.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key_pem = private_key.public_key().public_bytes(
    encoding=crypto_serialization.Encoding.PEM,
    format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# --- Actor Definition ---
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

# --- Server Initialization ---
app = ActivityPubServer()

# --- Key Retrieval Function ---
# This function provides the private key for signing outgoing activities.
async def get_keys_for_actor(identifier: str) -> list[ActorKey]:
    if identifier == USER_ID:
        return [ActorKey(key_id=actor.publicKey.id, private_key=private_key)]
    return []

# --- Endpoints ---
app.inbox("/users/{identifier}/inbox")

@app.get("/users/{identifier}")
async def get_actor_endpoint(identifier: str):
    if identifier == USER_ID:
        return ActivityResponse(actor)
    return JSONResponse({"error": "Not Found"}, status_code=404)

@app.webfinger()
async def webfinger_endpoint(request: Request, acct: WebfingerResource) -> Response:
    if acct.username == "demo" and acct.host == HOST:
        link = WebfingerLink(
            rel="self",
            type="application/activity+json",
            href=f"https://{HOST}/users/{USER_ID}"
        )
        wf_result = WebfingerResult(subject=acct, links=[link])
        return JSONResponse(wf_result.to_json(), media_type="application/jrd+json")
    return JSONResponse({"message": "Not Found"}, status_code=404)

@app.nodeinfo("/nodeinfo/2.1", "2.1")
async def nodeinfo_endpoint():
    return ActivityResponse(
        Nodeinfo(
            version="2.1",
            software=NodeinfoSoftware(name="apkit-demo", version="0.1.0"),
            protocols=[NodeinfoProtocol.ACTIVITYPUB],
            services=NodeinfoServices(inbound=[], outbound=[]),
            openRegistrations=False,
            usage=NodeinfoUsage(users=NodeinfoUsageUsers(total=1)),
            metadata={},
        )
    )

# --- Activity Handlers ---
@app.on(Follow)
async def on_follow_activity(ctx: Context):
    activity = ctx.activity
    if not isinstance(activity, Follow):
        return JSONResponse({"error": "Invalid activity type"}, status_code=400)

    # Resolve the actor who sent the Follow request
    follower_actor = None
    if isinstance(activity.actor, str):
        async with ActivityPubClient() as client:
            follower_actor = await client.actor.fetch(activity.actor)
    elif isinstance(activity.actor, APKitActor):
        follower_actor = activity.actor

    if not follower_actor:
        return JSONResponse({"error": "Could not resolve follower actor"}, status_code=400)

    # Automatically accept the follow request
    accept_activity = activity.accept()

    # Send the signed Accept activity back to the follower's inbox
    await ctx.send(
        get_keys_for_actor,
        follower_actor,
        accept_activity
    )
    return Response(status_code=202)

```
