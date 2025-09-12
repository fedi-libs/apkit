from typing import Any, Awaitable, Callable, Union, TYPE_CHECKING
import logging

import apmodel
from fastapi import Request, Response

from ..types import Context

if TYPE_CHECKING:
    from ..app import ActivityPubServer

logger = logging.getLogger("activitypub.server.outbox")


def create_outbox_route(
    apkit: "ActivityPubServer", f: Callable[[Context], Awaitable[Any]]
):
    async def on_outbox_internal(request: Request) -> Union[dict, Response]:
        response = await f(
            Context(_apkit=apkit, request=request, activity=apmodel.Activity())
        )
        return response

    return on_outbox_internal
