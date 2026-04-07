from typing import TYPE_CHECKING, Optional, Union

from apmodel.base import AS2Model
from apmodel.webfinger import Resource, Result

from . import _common

if TYPE_CHECKING:
    from .client import ActivityPubClient


class ActorResolver:
    def __init__(
        self,
        client: "ActivityPubClient",
        username: str,
        host: str,
        headers: Optional[dict] = None,
    ):
        self.__client = client
        self.__username = username
        self.__host = host
        self.__headers = headers or {"Accept": "application/jrd+json"}

    def __enter__(self) -> Result:
        headers = _common.reconstruct_headers(self.__headers, self.__client._user_agent)
        resource = Resource(username=self.__username, host=self.__host)
        url = _common.build_webfinger_url(host=self.__host, resource=resource)

        with self.__client.get(url, headers=headers) as resp:
            if 200 <= resp.raw.status_code < 400:
                data = resp.json()
                result = Result.from_dict(data)
                _common.validate_webfinger_result(result, resource)
                return result
            raise ValueError(
                f"Failed to resolve Actor: {url} (Status: {resp.raw.status_code})"
            )

    async def __aenter__(self) -> Result:
        headers = _common.reconstruct_headers(self.__headers, self.__client._user_agent)
        resource = Resource(username=self.__username, host=self.__host)
        url = _common.build_webfinger_url(host=self.__host, resource=resource)

        async with self.__client.get(url, headers=headers) as resp:
            if resp.raw.ok:
                data = await resp.json()
                result = Result.from_dict(data)
                _common.validate_webfinger_result(result, resource)
                return result
            raise ValueError(f"Failed to resolve Actor: {url}")

    def __exit__(self, *args):
        pass

    async def __aexit__(self, *args):
        pass


class ActorFetcher:
    def __init__(
        self, client: "ActivityPubClient", url: str, headers: Optional[dict] = None
    ):
        self.__client = client
        self.__url = url
        self.__headers = headers or {"Accept": "application/activity+json"}

    def __enter__(self) -> Union[AS2Model, dict, list, str, None]:
        headers = _common.reconstruct_headers(self.__headers, self.__client._user_agent)
        with self.__client.get(self.__url, headers=headers) as resp:
            if 200 <= resp.raw.status_code < 400:
                return resp.parse()
            raise ValueError(f"Failed to fetch Actor: {self.__url}")

    async def __aenter__(self) -> Union[AS2Model, dict, list, str, None]:
        headers = _common.reconstruct_headers(self.__headers, self.__client._user_agent)
        async with self.__client.get(self.__url, headers=headers) as resp:
            if resp.raw.ok:
                return await resp.parse()
            raise ValueError(f"Failed to fetch Actor: {self.__url}")

    def __exit__(self, *args):
        pass

    async def __aexit__(self, *args):
        pass


class ActorClient:
    def __init__(self, client: "ActivityPubClient"):
        self.__client = client

    def resolve(
        self, username: str, host: str, headers: Optional[dict] = None
    ) -> ActorResolver:
        return ActorResolver(self.__client, username, host, headers)

    def fetch(self, url: str, headers: Optional[dict] = None) -> ActorFetcher:
        return ActorFetcher(self.__client, url, headers)
