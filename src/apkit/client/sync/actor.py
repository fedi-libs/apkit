from typing import TYPE_CHECKING, Union

from apmodel.types import ActivityPubModel
from .. import _common, models

if TYPE_CHECKING:
    from .client import ActivityPubClient


class ActorFetcher:
    def __init__(self, client: "ActivityPubClient"):
        self.__client: "ActivityPubClient" = client

    def resolve(self, username: str, host: str) -> models.WebfingerResult:
        """Resolves an actor's profile from a remote server."""
        resource = models.Resource(username=username, host=host)
        url = _common.build_webfinger_url(host=host, resource=resource)

        resp = self.__client.get(url)
        if resp.ok:
            data = resp.json()
            result = models.WebfingerResult.from_dict(data)
            _common.validate_webfinger_result(result, resource)
            return result
        else:
            raise ValueError(f"Failed to resolve Actor: {url}")

    def fetch(self, url: str) -> Union[ActivityPubModel, dict]:
        resp = self.__client.get(url, headers={"User-Agent": "apkit/0.3.0", "Accept": "application/activity+json"})
        if resp.ok:
            data = resp.parse()
            return data
        else:
            raise ValueError(f"Failed to resolve Actor: {url}")