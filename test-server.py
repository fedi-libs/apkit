from apmodel import Create, Multikey, Person
from apmodel.vocab.object import Note
from apmodel.nodeinfo.ni21.nodeinfo import NodeInfo, Software
from apmodel.schema.propertyvalue import PropertyValue
from apmodel.security.cryptographickey import CryptographicKey
from apsig import KeyUtil
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from apkit import APKit
from apkit.x.starlette import ActivityPubMiddleware

ap = APKit()
priv = rsa.generate_private_key(key_size=2048, public_exponent=65537)
ed_privatekey = ed25519.Ed25519PrivateKey.generate()
keyutl = KeyUtil(private_key=ed_privatekey)
act = Person(
    id="https://test2.amase.cc/actor",
    preferredUsername="test",
    publicKey=CryptographicKey(
        id="https://test2.amase.cc/actor#main-key",
        owner="https://test2.amase.cc/actor",
        publicKeyPem=priv.public_key()
        .public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        .decode("utf-8"),
    ),  # type: ignore
    assertionMethod=[
        Multikey(
            id="https://test2.amase.cc/actor#ed25519-key",
            controller="https://test2.amase.cc/actor",
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
)

note = Note(
    id='https://test2.amase.cc/notes/1', 
    attributedTo="https://test2.amase.cc/actor",
    content='<p>投稿内容</p><br><a href="https://example.com">example.com</a>',
    to=[
        'https://www.w3.org/ns/activitystreams#Public'
    ]
)


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


@ap.on_create()
async def inbox(request: Request, activity: Create):
    pass


app = Starlette(middleware=[Middleware(ActivityPubMiddleware, apkit=ap)])

@app.route("/notes/1", methods=["GET"])
async def notes_1(request: Request):
    return JSONResponse(content=note.to_dict(), media_type="application/activity+json")

@app.route("/actor", methods=["GET"])
async def actor(request: Request):
    return JSONResponse(content=act.to_dict(), media_type="application/activity+json")


@app.route("/.well-known/webfinger", methods=["GET"])
async def webfinger(request: Request):
    return JSONResponse(
        content={
            "subject": "acct:test@test2.amase.cc",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": "https://test2.amase.cc/actor",
                },
            ],
        }
    )


import uvicorn

uvicorn.run(app, port=3002)
