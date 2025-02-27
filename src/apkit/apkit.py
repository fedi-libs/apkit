from typing import Optional

from apmodel import (
    Accept,
    Announce,
    Block,
    Create,
    Delete,
    Follow,
    Like,
    Reject,
    Undo,
    Update,
)
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

        self.config: Config = config if config else Config()

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
            self.nodeinfo_funcs[version] = func
            print(self.nodeinfo_funcs)
            return func

        return decorator

    def on_create(self):
        def decorator(func):
            self.activity_funcs[Create] = func
            return func

        return decorator

    def on_undo(self):
        def decorator(func):
            self.activity_funcs[Undo] = func
            return func

        return decorator

    def on_accept(self):
        def decorator(func):
            self.activity_funcs[Accept] = func
            return func

        return decorator

    def on_reject(self):
        def decorator(func):
            self.activity_funcs[Reject] = func
            return func

        return decorator

    def on_like(self):
        def decorator(func):
            self.activity_funcs[Like] = func
            return func

        return decorator

    def on_delete(self):
        def decorator(func):
            self.activity_funcs[Delete] = func
            return func

        return decorator

    def on_update(self):
        def decorator(func):
            self.activity_funcs[Update] = func
            return func

        return decorator

    def on_follow(self):
        def decorator(func):
            self.activity_funcs[Follow] = func
            return func

        return decorator

    def on_announce(self):
        def decorator(func):
            self.activity_funcs[Announce] = func
            return func

        return decorator

    def on_block(self):
        def decorator(func):
            self.activity_funcs[Block] = func
            return func

        return decorator
