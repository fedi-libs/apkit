from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from apmodel import Activity
from apmodel.types import ActivityPubModel
from apmodel.vocab.activity import Accept, Reject
from apmodel.vocab.actor import Actor, ActorEndpoints
from fastapi import Request

from ..client.client import ActivityPubClient
from ..types import ActorKey, Outbox  # noqa: F401

if TYPE_CHECKING:
    from .app import ActivityPubServer


@dataclass
class Context:
    _apkit: "ActivityPubServer"

    activity: Activity
    request: Request

    async def send(
        self, keys: List[ActorKey], target: Actor, activity: ActivityPubModel
    ):
        async with ActivityPubClient() as client:
            inbox = target.inbox
            priv_key = None
            key_id = None

            if (
                isinstance(target.endpoints, ActorEndpoints)
                and target.endpoints.shared_inbox
            ):
                if not isinstance(activity, (Accept, Reject)):
                    inbox = target.endpoints.shared_inbox
            if not isinstance(inbox, str):
                raise ValueError(f"Unsupported Inbox Type: {inbox}")

            if priv_key and key_id and inbox:
                async with client.post(
                    inbox, sign_as=keys, json=activity
                ) as _:
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
