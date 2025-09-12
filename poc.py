from typing import List
import uuid

from fastapi import Response, Request

from apkit.client.models import Resource, WebfingerResult
from apkit.client.models import Link as WebfingerLink
from apkit.server import ActivityPubServer, SubRouter
from apkit.server.responses import ActivityResponse
from apkit.models import (
    Follow,
    NodeinfoUsageUsers,
    Nodeinfo,
    NodeinfoProtocol,
    NodeinfoServices,
    NodeinfoSoftware,
    NodeinfoUsage,
    Undefined,
    Actor,
    Person,
    Object,
    CryptographicKey,
    Multikey
)
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.backends import default_backend

from fastapi.responses import JSONResponse
import uvicorn

from apkit.client.asyncio.client import ActivityPubClient
from apkit.config import AppConfig
from apkit.server.types import Context, ActorKey

HOST = "apsig.amase.cc"
USER_ID = str(uuid.uuid4())

ed_privatekey = ed25519.Ed25519PrivateKey.generate()
rsa_privatekey = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend()
)

async def get_actor_keys(identifier: str) -> List[ActorKey]:
    return [
        ActorKey(
            key_id=f"https://{HOST}/users/{USER_ID}#main-key",
            private_key=rsa_privatekey
        ),
        ActorKey(
            key_id=f"https://{HOST}/users/{USER_ID}#ed25519-key",
            private_key=ed_privatekey
        )
    ]

app = ActivityPubServer(
    apkit_config=AppConfig(
        actor_keys=get_actor_keys
    )
)
sub = SubRouter()
actor = Person(
    id=f"https://{HOST}/users/{USER_ID}",
    name="apkit demo",
    preferredUsername="demo",
    summary="Hi!",
    inbox=f"https://{HOST}/users/{USER_ID}/inbox",
    publicKey=CryptographicKey(
        id=f"https://{HOST}/users/{USER_ID}#main-key",
        owner=f"https://{HOST}/users/{USER_ID}",
        publicKeyPem=rsa_privatekey.public_key()
    ),
    assertionMethod=[
        Multikey(
            id=f"https://{HOST}/users/{USER_ID}#main-key",
            controller=f"https://{HOST}/users/{USER_ID}",
            publicKeyMultibase=rsa_privatekey.public_key()
        ),
        Multikey(
            id=f"https://{HOST}/users/{USER_ID}#ed25519-key",
            controller=f"https://{HOST}/users/{USER_ID}",
            publicKeyMultibase=ed_privatekey.public_key()
        )
    ]
)

async def nodeinfo_20():
    return ActivityResponse(
        Nodeinfo(
            version="2.0",
            software=NodeinfoSoftware("test", "0.1.0"),
            protocols=[NodeinfoProtocol.ACTIVITYPUB],
            services=NodeinfoServices(inbound=[], outbound=[]),
            openRegistrations=False,
            usage=NodeinfoUsage(
                users=NodeinfoUsageUsers(total=0, activeHalfyear=0, activeMonth=0),
                localComments=0,
                localPosts=0,
            ),
            metadata={},
        )
    )


app.inbox("/inbox", "/users/{identifier}/inbox")
app.outbox("/{identifier}/outbox")
sub.nodeinfo("/ni/2.0", "2.0", func=nodeinfo_20)

@app.webfinger()
async def webfinger(request: Request, acct: Resource) -> Response:
    if acct.username == "demo" and acct.host == "apsig.amase.cc":
        return JSONResponse(WebfingerResult(acct,links=[WebfingerLink("self", "application/activity+json", f"https://apsig.amase.cc/users/{USER_ID}")]).to_json(), media_type="application/jrd+json")
    else:
        return JSONResponse({"message": "Not Found"}, status_code=404)
    
@app.get("/users/{identifier}")
async def get_actor(request: Request, identifier: str) -> Response:
    if identifier == USER_ID:
        return ActivityResponse(actor)
    else:
        return JSONResponse({"message": "Not Found"}, status_code=404)

@app.on(Follow)
async def on_follow(ctx: Context) -> JSONResponse:
    if not isinstance(ctx.activity, Follow):
        return JSONResponse({"message": "Not Acceptable"}, 406)
    follow: Follow = ctx.activity
    if isinstance(follow.actor, str):
        async with ActivityPubClient() as client:
            resp = await client.actor.fetch(follow.actor)
            if isinstance(resp, Actor):
                follow.actor = resp
    if isinstance(follow.object, str):
        async with ActivityPubClient() as client:
            resp = await client.actor.fetch(follow.object)
            if isinstance(resp, Object):
                follow.object = resp
    if not isinstance(follow.actor, Actor) or not isinstance(follow.object, Object):
        print(type(follow.actor))
        print(type(follow.object))
        print("Object follow.actor or follow.object is not a Actor/Object.")
        return JSONResponse({"message": "Not Acceptable"}, 406)
    if follow.id is Undefined or follow.actor.id is Undefined or not follow.object.id:
        print("Id is not defined")
        print(f"followId: {follow.id}")
        print(f"targetId: {follow.actor.id}")
        print(f"ObjectId: {follow.object.id}")
        return JSONResponse({"message": "Not Acceptable"}, 406)
    
    if follow.object.id != f"https://{HOST}/users/{USER_ID}":
        return JSONResponse({"message": "Not Found"}, status_code=404)

    keys = await ctx.get_actor_keys(ctx.request.path_params.get("identifier", None))
    await ctx.send(
        keys,
        follow.actor,
        follow.accept(f"https://{HOST}/#accepts/{str(uuid.uuid4())}", follow.object.id) # pyright: ignore[reportArgumentType]
    )
    return JSONResponse({"message": "Hi!"}, status_code=201)

@app.nodeinfo("/nodeinfo/2.1", "2.1")
async def nodeinfo_21():
    return ActivityResponse(
        Nodeinfo(
            version="2.0",
            software=NodeinfoSoftware(
                "test",
                "0.1.0",
                "https://github.com/fedi-libs/apkit",
                "https://github.com/fedi-libs/apkit",
            ),
            protocols=[NodeinfoProtocol.ACTIVITYPUB],
            services=NodeinfoServices(inbound=[], outbound=[]),
            openRegistrations=False,
            usage=NodeinfoUsage(
                users=NodeinfoUsageUsers(total=0, activeHalfyear=0, activeMonth=0),
                localComments=0,
                localPosts=0,
            ),
            metadata={},
        )
    )


app.include_router(sub)

print(f"Actor ID is: {USER_ID}")
print(f"Server running in: https://{HOST}")
print(f"Server running in: https://{HOST}/users/{USER_ID}")
uvicorn.run(app, host="0.0.0.0", port=8000)
