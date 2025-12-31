from typing import TYPE_CHECKING

from apmodel.types import ActivityPubModel

from .. import _common, models

if TYPE_CHECKING:
    from .client import ActivityPubClient


class ActorFetcher:
    def __init__(self, client: "ActivityPubClient"):
        self.__client: "ActivityPubClient" = client

    def resolve(
        self,
        username: str,
        host: str,
        headers: dict = {"Accept": "application/jrd+json"},
    ) -> models.WebfingerResult:
        """Resolves an actor's profile from a remote server."""
        headers = _common.reconstruct_headers(headers, self.__client.user_agent)
        resource = models.Resource(username=username, host=host)
        url = _common.build_webfinger_url(host=host, resource=resource)

        resp = self.__client.get(url, headers=headers)
        if resp.ok:
            data = resp.json()
            result = models.WebfingerResult.from_dict(data)
            _common.validate_webfinger_result(result, resource)
            return result
        else:
            raise ValueError(f"Failed to resolve Actor: {url}")

    def fetch(
        self, url: str, headers: dict = {"Accept": "application/activity+json"}
    ) -> ActivityPubModel | dict | list | str | None:
        headers = _common.reconstruct_headers(headers, self.__client.user_agent)
        resp = self.__client.get(
            url,
            headers=headers,
        )
        if resp.ok:
            data = resp.parse()
            return data
        else:
            raise ValueError(f"Failed to resolve Actor: {url}")
