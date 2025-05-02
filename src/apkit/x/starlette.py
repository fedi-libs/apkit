# apkit Starlette integration
import re

from apmodel import StreamsLoader, Activity
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..apkit import APKit
from ..actor.fetch import ActorGetter
from ..integration.shared.signature import SignatureLib
from ..webfinger import Resource

class ActivityPubMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, apkit: APKit):
        super().__init__(app)
        self.apkit = apkit
        self.config = apkit.config
        self.versions = list(self.apkit.nodeinfo_funcs.keys())
        self.getter = ActorGetter(config=self.config)
        self.signature = SignatureLib(config=self.config)

    async def dispatch(self, request: Request, call_next):
        req = request
        if request.url.path == "/.well-known/host-meta":
            host_meta = (
                f"""
<?xml version="1.0"?>
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
    <Link rel="lrdd" type="application/xrd+xml" template="https://{request.base_url.hostname}{f":{request.base_url.port}" if request.base_url.port and request.base_url.port != 80 else ""}/.well-known/webfinger?resource="""
                + """{uri}" />
</XRD>"""
            )
            return Response(content=host_meta, media_type="application/xrd+xml")
        elif request.url.path == "/.well-known/webfinger":
            if self.apkit.webfinger_func:
                if request.query_params.get("resource"):
                    return await self.apkit.webfinger_func(request, resource=Resource().parse(request.query_params.get("resource"))) # type: ignore
                else:
                    response = await call_next(req)
                    return response
        elif any(re.match(path, request.url.path) for path in self.config.inbox_urls):
            body = await req.json()
            activity = StreamsLoader.load(body)
            if isinstance(activity, Activity):
                func = self.apkit.activity_funcs.get(type(activity))
                if func:
                    sign_result = await self.signature.verify(body, str(req.url), req.method, dict(req.headers))
                    if sign_result:
                        resp = await func(req, activity)
                        return resp
                    else:
                        return JSONResponse({"message": "Signature Verification Failed"}, status_code=401)
                else:
                    response = await call_next(req)
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
        response = await call_next(req)
        return response
