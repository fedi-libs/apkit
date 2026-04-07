from typing import Mapping

from apmodel.base import AS2Model
from apmodel.nodeinfo.nodeinfo import Nodeinfo
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


class ActivityResponse(JSONResponse):
    media_type = "application/activity+json; charset=utf-8"

    def __init__(
        self,
        content: AS2Model | Nodeinfo,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: AS2Model | Nodeinfo) -> bytes:
        if isinstance(content, AS2Model):
            rendered = content.dump()
        else:
            rendered = content.model_dump()
        return super().render(rendered)
