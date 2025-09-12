import functools

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.routing import NoMatchFound

@functools.cache
def nodeinfo_links(request: Request):
    links = []

    try:
        ni20_url = request.url_for("__apkit_nodeinfo_2.0")
        links.append({
            "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
            "href": str(ni20_url)
        })
    except NoMatchFound:
        pass

    try:
        ni21_url = request.url_for("__apkit_nodeinfo_2.1")
        links.append({
            "rel": "http://nodeinfo.diaspora.software/ns/schema/2.1",
            "href": str(ni21_url)
        })
    except NoMatchFound:
        pass

    return JSONResponse({
        "links": links
    })

def nodeinfo_links_route(request: Request) -> JSONResponse:
    return nodeinfo_links(request) # pyright: ignore[reportArgumentType]