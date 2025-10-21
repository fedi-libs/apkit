import json
import sys
from typing import Callable, Dict, Union, TYPE_CHECKING
import logging

import apmodel
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from ..types import Context
from ...config import AppConfig
from ...helper.inbox import InboxVerifier

if TYPE_CHECKING:
    from ..app import ActivityPubServer

logger = logging.getLogger('activitypub.server.inbox')
handler = logging.StreamHandler(sys.stdout)     # <-----------------------
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def create_inbox_route(apkit: "ActivityPubServer", config: AppConfig, routes: Dict[type[apmodel.Activity], Callable]):
    async def on_inbox_internal(request: Request) -> Union[dict, Response]:
        verifier = InboxVerifier(config)
        body = await request.body()
        activity = apmodel.load(json.loads(body))
        if isinstance(activity, apmodel.Activity) and (isinstance(activity.object, apmodel.Object) or isinstance(activity.object, str)):
            func = routes.get(type(activity))

            if func:
                verify_result = await verifier.verify(body, str(request.url), request.method, dict(request.headers))
                if verify_result:
                    logger.debug(f"Activity received: {type(activity)}")
                    response = await func(ctx=Context(_apkit=apkit, request=request, activity=activity))
                    return response
                else:
                    return JSONResponse({"message": "Signature Verification Failed"}, status_code=401)
            else:
                logger.debug(f"Activity received but no handler registered for activity type {type(activity)}")
                return JSONResponse({"message": "Ok"}, status_code=200)
        return JSONResponse({"message": "Body is not Activity"}, status_code=400)
    return on_inbox_internal
