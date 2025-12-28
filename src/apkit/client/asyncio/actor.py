from typing import TYPE_CHECKING

from apmodel.types import ActivityPubModel

from .. import _common, models

if TYPE_CHECKING:
    from .client import ActivityPubClient


class ActorFetcher:
    def __init__(self, client: "ActivityPubClient"):
        self.__client: "ActivityPubClient" = client

    async def resolve(
        self,
        username: str,
        host: str,
        headers: dict = {"Accept": "application/jrd+json"},
    ) -> models.WebfingerResult:
        """Resolves an actor's profile from a remote server asynchronously."""
        headers = _common.reconstruct_headers(headers, self.__client.user_agent)
        resource = models.Resource(username=username, host=host)
        url = _common.build_webfinger_url(host=host, resource=resource)

        async with self.__client.get(url, headers=headers) as resp:
            if resp.ok:
                data = await resp.json()
                result = models.WebfingerResult.from_dict(data)
                _common.validate_webfinger_result(result, resource)
                return result
            else:
                raise ValueError(f"Failed to resolve Actor: {url}")

    async def fetch(
        self, url: str, headers: dict = {"Accept": "application/activity+json"}
    ) -> ActivityPubModel | dict | list | str | None:
        headers = _common.reconstruct_headers(
            headers if headers else {}, self.__client.user_agent
        )
        async with self.__client.get(url, headers=headers) as resp:
            if resp.ok:
                data = await resp.parse()
                return data
            else:
                raise ValueError(f"Failed to resolve Actor: {url}")
