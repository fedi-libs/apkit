from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Union, Literal

from ..types import Outbox
from ..models import Activity

class AbstractApkitIntegration(ABC):
    @abstractmethod
    def outbox(self, *args) -> None: ...
    
    @abstractmethod
    def inbox(self, *args) -> None: ...
    
    @abstractmethod
    def on(self, type: Union[type[Activity], type[Outbox]], func: Optional[Callable] = None) -> Any:
        def decorator(func: Callable) -> Callable: ...
    
    @abstractmethod
    def webfinger(self, func: Optional[Callable] = None) -> Any:
        def decorator(func: Callable) -> Callable: ...

    @abstractmethod
    def nodeinfo(
        self,
        route: str,
        version: Literal["2.0", "2.1"],
        func: Optional[Callable] = None,
    ) -> Any:
        def decorator(fn: Callable) -> Callable: ...
        