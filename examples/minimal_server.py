import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization
import os
import sys

from apkit.server import ActivityPubServer
from apkit.server.types import Context, ActorKey, Outbox
from apkit.server.responses import ActivityResponse
from apkit.models import (
    Person,
    CryptographicKey,
    Follow,
    Actor as APKitActor,
    Nodeinfo,
    NodeinfoSoftware,
    NodeinfoProtocol,
    NodeinfoServices,
    NodeinfoUsage,
    NodeinfoUsageUsers,
    OrderedCollection,
    OrderedCollectionPage,
)
from apkit.client import WebfingerResource, WebfingerResult, WebfingerLink
from apkit.client.asyncio.client import ActivityPubClient

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
HOST = os.getenv("APKIT_DOMAIN")
if HOST is None:
    logger.error(
        "Environnment variable APKIT_DOMAIN is not set. See README.md how to set the variable."
    )
    sys.exit(1)

logger.info(f"Using {HOST} as host name.")

USER_ID = "demo"

logger.info(
    f"You can now find the actor by searching for @{USER_ID}@{HOST} on the Fediverse."
)

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
        publicKeyPem=public_key_pem,
    ),
)

# --- Server Initialization ---
app = ActivityPubServer()


# --- Key Retrieval Function ---
# This function provides the private key for signing outgoing activities.
def get_keys_for_actor(identifier: str) -> list[ActorKey]:
    if identifier == USER_ID:
        return [ActorKey(key_id=actor.publicKey.id, private_key=private_key)]
    return []


# --- Endpoints ---
app.inbox("/users/{identifier}/inbox")
app.outbox("/users/{identifier}/outbox")


@app.get("/users/{identifier}")
async def get_actor_endpoint(identifier: str):
    if identifier == USER_ID:
        return ActivityResponse(actor)
    return JSONResponse({"error": "Not Found"}, status_code=404)


@app.webfinger()
async def webfinger_endpoint(request: Request, acct: WebfingerResource) -> Response:
    if acct.username == USER_ID and acct.host == HOST:
        link = WebfingerLink(
            rel="self",
            type="application/activity+json",
            href=f"https://{HOST}/users/{USER_ID}",
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

@app.on(Outbox)
async def outbox(ctx: Context):
    identifier = ctx.request.path_params.get("identifier")

    if identifier != USER_ID:
        return Response(status_code=404)

    if not ctx.request.query_params.get("page"):
        outbox = OrderedCollection()
        outbox.totalItems = 0  # No letter in the mail today.
        outbox.id = f"https://{HOST}/users/{identifier}/outbox"
        outbox.first = f"{outbox.id}?page=true"
        outbox.last = f"{outbox.id}?min_id=0&page=true"
    else:
        outbox = OrderedCollectionPage()

    return ActivityResponse(outbox)

# --- Activity Handlers ---
@app.on(Follow)
async def on_follow_activity(ctx: Context) -> Response:
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
        return JSONResponse(
            {"error": "Could not resolve follower actor"}, status_code=400
        )

    logger.info(f"🫂 {follower_actor.name} follows me.")

    # Automatically accept the follow request
    id_ = "https://{HOST}/activity/{uuid.uuid4()}"
    accept_activity = activity.accept(id_, actor)

    # Send the signed Accept activity back to the follower's inbox
    keys = get_keys_for_actor(USER_ID)
    await ctx.send(keys, follower_actor, accept_activity)
    return Response(status_code=202)
