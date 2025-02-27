from typing import Optional

from apmodel import Actor, StreamsLoader

from ..req.request import APRequest, Config


class ActorGetter:
    def __init__(self, config: Config | None = None) -> None:
        self.req: APRequest = APRequest(Config()) if not config else APRequest(config)

    async def fetch(
        self,
        username: Optional[str] = None,
        host: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Optional[Actor]:
        if username and host:
            resp = await self.req.get(
                f"https://{host}/.well-known/webfinger?resource=acct:{username}@{host}"
            )
            if resp:
                rj = await resp.json()
                if rj.get("subject") == f"acct:{username}@{host}":
                    if rj.get("links"):
                        for link in rj["links"]:
                            if link["rel"] == "self":
                                if link["type"] == "application/activity+json":
                                    actor = await self.req.get(link["href"])
                                    if actor:
                                        actor_json = await actor.json()
                                        loaded = StreamsLoader.load(actor_json)
                                        if isinstance(loaded, Actor):
                                            return loaded
        elif url:
            actor = await self.req.get(url, headers={"Accept": "application/activity+json"})
            if actor:
                actor_json = await actor.json()
                loaded = StreamsLoader.load(actor_json)
                if isinstance(loaded, Actor):
                    return loaded
        else:
            raise Exception
