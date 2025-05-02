import functools
from typing import Optional

from apmodel.nodeinfo.ni20.nodeinfo import (
    NodeInfo,
    ProtocolEnum,
    Services,
    Software,
    Usage,
    Users,
)

from .config import Config


class APKit:
    def __init__(
        self,
        name: str = "APKit",
        description: str = "Powerful Toolkit for ActivityPub Implementations.",
        version: str = "0.1.0",
        config: Optional[Config] = None,
    ):
        self.name = name
        self.description = description
        self.version = version

        self.nodeinfo_funcs = {"2.0": self.default_nodeinfo}

        self.activity_funcs: dict = {}
        self.inbox_func = None
        self.webfinger_func = None

        self.config: Config = config if config else Config()
        self.config.compile()

    async def default_nodeinfo(self) -> NodeInfo | dict:
        return NodeInfo(
            software=Software(name=self.name, version=self.version),
            protocols=[ProtocolEnum.ACTIVITYPUB],
            services=Services(inbound=[], outbound=[]),
            open_registrations=False,
            usage=Usage(users=Users(0, 0, 0)),
            metadata={"nodeDescription": self.description},
        )

    def nodeinfo(self, version: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.nodeinfo_funcs[version] = wrapper
            return wrapper
        return decorator

    def inbox(self):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.inbox_func = wrapper
            return wrapper

        return decorator

    def webfinger(self):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.webfinger_func = wrapper
            return wrapper

        return decorator
    
    def on(self, type):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.activity_funcs[type] = wrapper
            return wrapper

        return decorator