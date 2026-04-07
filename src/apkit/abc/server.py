from abc import ABC, abstractmethod
from typing import Any, Callable, Literal, Optional, Union

from ..models import Activity
from ..types import Outbox


class AbstractApkitIntegration(ABC):
    @abstractmethod
    def outbox(self, *args) -> None: ...

    @abstractmethod
    def inbox(self, *args) -> None: ...

    @abstractmethod
    def on(
        self,
        type: Union[type[Activity], type[Outbox]],
        func: Optional[Callable] = None,
    ) -> Any: ...

    @abstractmethod
    def webfinger(self, func: Optional[Callable] = None) -> Any: ...

    @abstractmethod
    def nodeinfo(
        self,
        route: str,
        version: Literal["2.0", "2.1"],
        func: Optional[Callable] = None,
    ) -> Any: ...
