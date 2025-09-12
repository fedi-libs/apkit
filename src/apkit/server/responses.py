from typing import Mapping

from apmodel.types import ActivityPubModel
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask

class ActivityResponse(JSONResponse):
    media_type = "application/activity+json; charset=utf-8"

    def __init__(self, content: ActivityPubModel, status_code: int = 200, headers: Mapping[str, str] | None = None, media_type: str | None = None, background: BackgroundTask | None = None) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: ActivityPubModel) -> bytes:
        return super().render(content.to_json())