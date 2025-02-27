import asyncio
import contextlib
import json
import random
import string
import sys
import uuid

import aiohttp
import uvicorn
from apmodel import Accept, Create, Multikey, Person
from apmodel.nodeinfo.ni21.nodeinfo import NodeInfo, Software
from apmodel.schema.propertyvalue import PropertyValue
from apmodel.security.cryptographickey import CryptographicKey
from apmodel.vocab.object import Note
from apsig import KeyUtil, draftSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from taskiq import InMemoryBroker

from apkit import APKit

ap = APKit()
broker = InMemoryBroker()

priv = rsa.generate_private_key(
    key_size=3072, public_exponent=65537, backend=default_backend()
)
ed_privatekey = ed25519.Ed25519PrivateKey.generate()


def generate_random_string(length):
    # 使用する文字のセット（英大文字、英小文字、数字）
    characters = string.ascii_letters + string.digits
    # ランダムな文字列を生成
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

random_str = generate_random_string(8)
actorId = str(uuid.uuid4())
noteId = str(uuid.uuid4())
print(actorId)
print(noteId)
keyutl = KeyUtil(private_key=ed_privatekey)
act = Person(
    id=f"https://test2.amase.cc/users/{actorId}",
    preferredUsername=random_str,
    publicKey=CryptographicKey(
        id=f"https://test2.amase.cc/users/{actorId}#main-key",
        owner=f"https://test2.amase.cc/users/{actorId}",
        publicKeyPem=priv.public_key()
        .public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        .decode("utf-8"),
    ),  # type: ignore
    assertionMethod=[
        Multikey(
            id=f"https://test2.amase.cc/users/{actorId}#ed25519-key",
            controller=f"https://test2.amase.cc/users/{actorId}",
            publicKeyMultibase=keyutl.encode_multibase(),
        )
    ],
    summary="Testing ActivityPub Toolkit (apkit)",
    attachment=[
        PropertyValue(
            name="GitHub",
            value='<p><a href="https://github.com/AmaseCocoa/apkit/">https://github.com/AmaseCocoa/apkit/</a></p>\n',
        )
    ],
    inbox="https://test2.amase.cc/inbox",
    sharedInbox="https://test2.amase.cc/inbox",
    to=["https://www.w3.org/ns/activitystreams#Public"],
)

note = Note(
    id=f"https://test2.amase.cc/notes/{noteId}",
    attributedTo=f"https://test2.amase.cc/users/{actorId}",
    content='<p>Testing APKit Inbox Post</p><br><a href="https://example.com">example.com</a>',
    to=["https://www.w3.org/ns/activitystreams#Public"],
)
created = Create(
    id=f"https://test2.amase.cc/notes/{noteId}/activity", object=note, actor=act.id
)
print(act.id)
post_base = "https://test1.amase.cc"
post_base = "https://mstdn.amase.cc"
post_base = "http://localhost:61685"

@broker.task
async def post_inbox() -> None:
    signer = draftSigner()
    created_dict = created.to_dict()
    headers = signer.sign(
        priv,
        "POST",
        f"{post_base}/inbox",  # https://test1.amase.cc
        headers={"Content-Type": "application/activity+json"},
        key_id=f"https://test2.amase.cc/users/{actorId}#main-key",
        body=json.dumps(created_dict, ensure_ascii=False).encode("utf-8"),
    )
    async with aiohttp.ClientSession(headers=headers) as session:
        print(headers)
        print("---")
        print(created_dict)
        print("---")
        async with session.post(
            f"{post_base}/inbox", json=created_dict
        ) as resp:  # https://test1.amase.cc
            print(await resp.text())
            print(resp.status)


@ap.nodeinfo("2.1")
async def nodeinfo():
    return NodeInfo(
        Software(
            "test",
            "0.1.0-dev.apkit",
            "https://github.com/AmaseCocoa/apkit",
            "https://ap.amase.cc",
        ),
        metadata={"nodeDescription": "An APKit Test Server"},
    )


@ap.on_accept()
async def accept(request: Request, accept: Accept):
    print(json.dumps(accept.to_dict(), ensure_ascii=False, indent=4))
    return Response(status_code=201)


@ap.on_create()
async def create(request: Request, activity: Create):
    pass


@contextlib.asynccontextmanager
async def lifespan(app):
    await broker.startup()
    yield
    await broker.shutdown()


app = Starlette(
    middleware=[],
    lifespan=lifespan,  # Middleware(ActivityPubMiddleware, apkit=ap)
)


@app.route("/api/notes/create", methods=["POST"])
async def create_post(request: Request):
    if request.headers.get("token") != "ebxBE7btjL":
        return Response(status_code=403)
    else:
        await post_inbox.kiq()
        return JSONResponse(content=note.to_dict(), media_type="application/json")


@app.route(f"/notes/{noteId}/activity", methods=["GET"])
async def notes_activity(request: Request):
    return JSONResponse(
        content=created.to_dict(), media_type="application/activity+json"
    )


@app.route(f"/notes/{noteId}", methods=["GET"])
async def notes_1(request: Request):
    return JSONResponse(content=note.to_dict(), media_type="application/activity+json")


@app.route(f"/users/{actorId}", methods=["GET"])
async def user(request: Request):
    return JSONResponse(content=act.to_dict(), media_type="application/activity+json")


@app.route("/inbox", methods=["POST"])
async def nibox(request: Request):
    print(request.headers)
    print("---")
    print(await request.json())
    print("---")
    return Response(status_code=503)


@app.route("/", methods=["GET"])
async def idx(request: Request):
    return Response("Hi")


@app.route("/.well-known/webfinger", methods=["GET"])
async def webfinger(request: Request):
    return JSONResponse(
        content={
            "subject": f"acct:{random_str}@test2.amase.cc",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"https://test2.amase.cc/users/{actorId}",
                },
            ],
        }
    )


uvicorn.run(app, port=3002)
