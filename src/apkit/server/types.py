from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from apmodel import Activity
from apmodel.vocab.activity import Accept, Reject
from apmodel.types import ActivityPubModel
from apmodel.vocab.actor import Actor, ActorEndpoints
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Request

from ..types import ActorKey
from ..client.asyncio.client import ActivityPubClient

if TYPE_CHECKING:
    from .app import ActivityPubServer

@dataclass
class Context:
    _apkit: "ActivityPubServer"

    activity: Activity
    request: Request

    async def send(self, keys: List[ActorKey], target: Actor, activity: ActivityPubModel):
        async with ActivityPubClient() as client:

            inbox = None
            priv_key = None
            key_id = None

            if target.endpoints is ActorEndpoints and target.endpoints.sharedInbox:
                if not isinstance(activity, Accept) and not isinstance(activity, Reject):
                    inbox = target.endpoints.sharedInbox
            else:
                inbox = target.inbox
            if not isinstance(inbox, str):
                raise ValueError("Unsupported Inbox Type")


            for key in keys:
                if isinstance(key.private_key, rsa.RSAPrivateKey):
                    priv_key = key.private_key
                    key_id = key.key_id
                    break
            if priv_key and key_id and inbox:
                async with client.post(inbox, key_id=key_id, signature=priv_key, json=activity) as resp:
                    return None
            else:
                pass

    async def get_actor_keys(self, identifier: Optional[str]) -> List[ActorKey]:
        if identifier:
            if self._apkit._get_actor_keys:
                actor_keys = await self._apkit._get_actor_keys(identifier)
                if actor_keys:
                    return actor_keys
        return []