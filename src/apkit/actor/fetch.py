from typing import Optional

from apmodel import Actor, load
from cryptography.hazmat.primitives.asymmetric import rsa

from ..request import ApRequest, SigType
from ..config import Config


class ActorGetter:
    def __init__(self, config: Config = Config(), sig_type: SigType = SigType.DRAFT, key_id: Optional[str] = None, private_key: Optional[rsa.RSAPrivateKey] = None) -> None:
        self.__config = {
            "config": config,
            "sig_type": sig_type,
            "key_id": key_id,
            "private_key": private_key,
        }
        self.config = config

    async def __get_actor(
        self,
        rj: dict,
        username: Optional[str] = None,
        host: Optional[str] = None,
    ) -> Actor | None:
        if rj.get("subject") == f"acct:{username}@{host}" and rj.get("links"):
            for link in rj["links"]:
                if (
                    link["rel"] == "self"
                    and link["type"] == "application/activity+json"
                ):
                    async with ApRequest(**self.__config) as req:
                        actor = await req.signed_get(link["href"], headers={"User-Agent": self.config.user_agent})
                        if actor:
                            actor_json = await actor.json()
                            loaded = load(actor_json)
                            if isinstance(loaded, Actor):
                                return loaded
        return None

    async def fetch(
        self,
        username: Optional[str] = None,
        host: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Optional[Actor]:
        if username and host:
            async with ApRequest(**self.__config) as req:
                resp = await req.signed_get(
                    f"https://{host}/.well-known/webfinger?resource=acct:{username}@{host}"
                )
                if resp:
                    rj = await resp.json()
                    return await self.__get_actor(rj, username, host)
        elif url:
            async with ApRequest(**self.__config) as req:
                actor = await req.signed_get(
                    url, headers={"User-Agent": self.config.user_agent, "Accept": "application/activity+json"}
                )
                if actor:
                    actor_json = await actor.json()
                    loaded = load(actor_json)
                    if isinstance(loaded, Actor):
                        return loaded
        else:
            raise Exception
