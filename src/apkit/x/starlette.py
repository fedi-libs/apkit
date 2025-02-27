# apkit Starlette integration
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

# import traceback
from cryptography.hazmat.primitives import serialization

from ..apkit import APKit
from ..sig.verify import Verifier
from ..actor.fetch import ActorGetter
from apmodel.loader import StreamsLoader
from apmodel.security.cryptographickey import CryptographicKey
from apmodel.cid.multikey import Multikey
from apmodel import Activity, Actor, Link
from apsig import ProofVerifier


class ActivityPubMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, apkit: APKit):
        super().__init__(app)
        self.apkit = apkit
        self.config = apkit.config
        self.versions = list(self.apkit.nodeinfo_funcs.keys())
        self.getter = ActorGetter(config=self.config)

    async def dispatch(self, request: Request, call_next):
        req = request
        if request.url.path == "/.well-known/host-meta":
            host_meta = f"""
<?xml version="1.0"?>
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
    <Link rel="lrdd" type="application/xrd+xml" template="https://{request.base_url.hostname}{f":{request.base_url.port}" if request.base_url.port and request.base_url.port != 80 else ""}/.well-known/webfinger?resource=""" + """{uri}" />
</XRD>"""
            return Response(content=host_meta, media_type="application/xrd+xml")
        elif request.url.path == "/inbox":  # Handle ActivityPub Endpoint
            proof_verified = False
            activity = StreamsLoader.load(await req.json())
            signature_header = req.headers.get("signature")
            signature_parts = {}
            if signature_header:
                for item in signature_header.split(","):
                    key, value = item.split("=", 1)
                    signature_parts[key.strip()] = value.strip().strip('"')
            if isinstance(activity, Activity):
                func = self.apkit.activity_funcs.get(type(activity))
                if func:
                    if isinstance(activity.actor, list):
                        if activity.actor != []:
                            if isinstance(activity.actor[0], str):
                                actor = await self.getter.fetch(url=activity.actor[0])
                            elif isinstance(activity.actor[0], Link):
                                actor = await self.getter.fetch(
                                    url=activity.actor[0].href  # type: ignore
                                )
                            elif isinstance(activity.actor, Actor):
                                actor = activity.actor
                    elif isinstance(activity.actor, str):
                        actor = await self.getter.fetch(url=activity.actor)
                    elif isinstance(activity.actor, Link):
                        actor = await self.getter.fetch(url=activity.actor.href)
                    elif isinstance(activity.actor, Actor):
                        actor = activity.actor
                    if actor:
                        if isinstance(actor.publicKey, CryptographicKey):
                            if actor.publicKey.id == signature_parts.get("keyId"):
                                key_id = actor.publicKey.id
                                key = actor.publicKey.publicKeyPem
                                key_txt = actor.publicKey.publicKeyPem.public_bytes(  # type: ignore
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                                ).decode("utf-8")
                        elif isinstance(actor.publicKey, dict):
                            if actor.publicKey["id"] == signature_parts.get("keyId"):
                                key_id = actor.publicKey["id"]
                                key_txt = actor.publicKey["publicKeyPem"]
                                key = serialization.load_pem_public_key(
                                    actor.publicKey["publicKeyPem"].encode("utf-8")
                                    if isinstance(actor.publicKey["publicKeyPem"], str)
                                    else actor.publicKey["publicKeyPem"]
                                )
                        body = await req.json()
                        if isinstance(activity, Activity):
                            if activity.proof:
                                if actor.assertionMethod:
                                    for key in actor.assertionMethod:
                                        if (
                                            isinstance(key, Multikey)
                                            and key.publicKeyMultibase
                                            and key.id
                                            == activity.proof.verificationMethod
                                        ):
                                            pv = ProofVerifier(
                                                key.publicKeyMultibase  # type: ignore
                                            )
                                            p = pv.verify_proof(body)
                                            if p.get("verified"):
                                                key_id = key.id
                                                key_txt = key.publicKeyMultibase
                                                proof_verified = True
                                                break
                        if not proof_verified:
                            verifier = Verifier()
                            verifyed = verifier.verify(
                                body,
                                key,  # type: ignore
                                req.method,
                                req.url.__str__(),
                                dict(req.headers),
                            )
                            if verifyed:
                                await self.config.kv.set(f"signature:{key_id}", key_txt)
                                response = await func(req, activity)
                                return response
                        else:
                            response = await func(req, activity)
                            return response
        elif request.url.path == "/.well-known/nodeinfo":
            links = []
            for v in self.versions:
                host = (
                    f"{request.url.hostname}:{request.url.port}"
                    if request.url.port and request.url.port != 80
                    else request.url.hostname
                )
                links.append(
                    {
                        "rel": f"http://nodeinfo.diaspora.software/ns/schema/{v}",
                        "href": f"{request.url.scheme}://{host}/nodeinfo/{v}",
                    }
                )
            return JSONResponse(content={"links": links})
        elif request.url.path.startswith("/nodeinfo/"):
            path_spritted = request.url.path.strip("/").split("/")
            try:
                if path_spritted[1] in self.versions:
                    nodeinfo = await self.apkit.nodeinfo_funcs[path_spritted[1]]()
                    headers = {
                        "Content-Type": f'application/json; profile="http://nodeinfo.diaspora.software/ns/schema/{path_spritted[1]}#"; charset=utf-8'
                    }
                    if isinstance(nodeinfo, dict):
                        return JSONResponse(content=nodeinfo, headers=headers)
                    return JSONResponse(content=nodeinfo.to_dict(), headers=headers)
            except Exception:  # noqa: E722
                pass
                # print(traceback.format_exc())
        response = await call_next(req)
        return response
