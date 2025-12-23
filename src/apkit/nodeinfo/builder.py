from typing import Literal, Optional, Union

from apmodel.nodeinfo.nodeinfo import (
    Nodeinfo,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoInbound as Inbound,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoOutbound as Outbound,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoProtocol as Protocol,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoServices as Services,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoSoftware as Software,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoUsage as Usage,  # noqa: F401
)
from apmodel.nodeinfo.nodeinfo import (
    NodeinfoUsageUsers as Users,  # noqa: F401
)


class NodeinfoBuilder:
    def __init__(self, version: Literal["2.1", "2.0"] = "2.1") -> None:
        self.version: Literal["2.1", "2.0"] = version

        self.__protocols = None
        self.__open_registrations = None
        self.__metadata = {}

        # nodeinfo.software
        self.__software_name = None
        self.__software_version = None
        self.__software_repository = None
        self.__software_homepage = None

        # nodeinfo.services
        self.__services_inbound = None
        self.__services_outbound = None

        # nodeinfo.usage
        self.__usage_users_total = None
        self.__usage_local_comments = None
        self.__usage_local_posts = None
        self.__usage_active_halfyear = None
        self.__usage_active_month = None

    def set_software(
        self,
        name: str,
        version: str,
        repository: Optional[str],
        homepage: Optional[str],
    ) -> "NodeinfoBuilder":
        self.__software_name = name
        self.__software_version = version
        self.__software_repository = repository
        self.__software_homepage = homepage
        return self

    def set_protocols(self, protocols: list[Union[str, Protocol]]) -> "NodeinfoBuilder":
        self.__protocols = protocols
        return self

    def set_services(
        self,
        inbound: list[Union[str, Inbound]],
        outbound: list[Union[str, Outbound]],
    ) -> "NodeinfoBuilder":
        self.__services_inbound = inbound
        self.__services_outbound = outbound
        return self

    def set_usage(
        self,
        users_total: int,
        local_comments: Optional[int] = None,
        local_posts: Optional[int] = None,
        active_halfyear: Optional[int] = None,
        active_month: Optional[int] = None,
    ) -> "NodeinfoBuilder":
        self.__usage_users_total = users_total
        self.__usage_local_comments = local_comments
        self.__usage_local_posts = local_posts
        self.__usage_active_halfyear = active_halfyear
        self.__usage_active_month = active_month
        return self

    def set_open_registrations(self, status: bool) -> "NodeinfoBuilder":
        self.__open_registrations = status
        return self

    def set_metadata(self, metadata: dict) -> "NodeinfoBuilder":
        self.__metadata = metadata
        return self

    def build(self) -> Nodeinfo:
        if not self.__software_name or not self.__software_version:
            raise ValueError(
                "Software name and version are mandatory fields for Nodeinfo."
            )

        if not self.__protocols:
            raise ValueError("Protocols list cannot be empty.")

        if self.__services_inbound is None or self.__services_outbound is None:
            raise ValueError("Both inbound and outbound services lists must be set.")

        if self.__usage_users_total is None:
            raise ValueError("Total number of users ('usage.users.total') must be set.")

        if self.__open_registrations is None:
            raise ValueError("'openRegistrations' must be set.")

        if self.version == "2.0":
            if self.__software_homepage or self.__software_repository:
                raise ValueError(
                    "Software homepage and repository fields are not defined in Nodeinfo version 2.0 by this implementation."
                )

        return Nodeinfo(
            version=self.version,
            software=Software(
                name=self.__software_name,
                version=self.__software_version,
                homepage=self.__software_homepage,
                repository=self.__software_repository,
            ),
            protocols=self.__protocols,
            services=Services(
                inbound=self.__services_inbound,
                outbound=self.__services_outbound,
            ),
            open_registrations=self.__open_registrations,
            usage=Usage(
                users=Users(
                    total=self.__usage_users_total,
                    activeHalfyear=self.__usage_active_halfyear,
                    activeMonth=self.__usage_active_month,
                ),
                localComments=self.__usage_local_comments,
                localPosts=self.__usage_local_posts,
            ),
            metadata=self.__metadata,
        )
