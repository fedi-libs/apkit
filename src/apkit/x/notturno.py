# apkit Notturno integration
from notturno import Request, Response
from notturno.middleware.base import BaseMiddleware

class ActivityPubMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, call_next):
        if request.url.path == "/inbox": # Handle ActivityPub Endpoint
            pass
        else:
            resp: Response = await call_next(request)
            return resp