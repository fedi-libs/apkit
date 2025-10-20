from dataclasses import dataclass
from typing import Any, List, Optional
from abc import ABC, abstractmethod

from apmodel import Activity
from apmodel.types import ActivityPubModel
from apmodel.vocab.actor import Actor

from ..types import ActorKey

@dataclass
class AbstractContext(ABC):
    activity: Activity
    request: Any

    @abstractmethod
    def send(self, keys: List[ActorKey], target: Actor, activity: ActivityPubModel): ...

    @abstractmethod
    def get_actor_keys(self, identifier: Optional[str]) -> List[ActorKey]: ...