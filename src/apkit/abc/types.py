from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional

from apmodel.base import AS2Model
from apmodel.core import Activity
from apmodel.objects import Actor

from ..types import ActorKey


@dataclass
class AbstractContext(ABC):
    activity: Activity
    request: Any

    @abstractmethod
    def send(self, keys: List[ActorKey], target: Actor, activity: AS2Model): ...

    @abstractmethod
    def get_actor_keys(self, identifier: Optional[str]) -> List[ActorKey]: ...
