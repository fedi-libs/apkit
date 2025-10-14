import re
from typing import Any, Dict, List, Union, Optional

from dataclasses import dataclass

@dataclass(frozen=True)
class Resource:
    """Represents a WebFinger resource."""

    username: str
    host: str
    url: Optional[str] = None

    def __str__(self) -> str:
        return f"acct:{self.username}@{self.host}"

    @classmethod
    def parse(cls, resource_str: str) -> "Resource":
        """Parses a resource string (e.g., 'acct:user@example.com')."""
        if resource_str.startswith("acct:"):
            resource_str = resource_str[5:]

        match = re.match(r"^([^@]+)@([^@]+)$", resource_str)
        if not match:
            return cls(username="", host="", url=resource_str)
            #raise ValueError(f"Invalid resource format: {resource_str}")

        username, host = match.groups()
        return cls(username=username, host=host, url=None)

    def export(self) -> str:
        return f"acct:{self.username}@{self.host}"

@dataclass(frozen=True)
class Link:
    """Represents a link in a WebFinger response."""

    rel: str
    type: str | None
    href: str | None

    def to_json(self) -> dict:
        return {
            "rel": self.rel,
            "type": self.type,
            "href": self.href
        }



@dataclass(frozen=True)
class WebfingerResult:
    """Represents a parsed WebFinger response."""

    subject: Resource
    links: List[Link]

    def to_json(self) -> dict:
        links = []
        for link in self.links:
            links.append(link.to_json())

        return {
            "subject": self.subject.export(),
            "links": links
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebfingerResult":
        """Parses a dictionary into a WebfingerResult object."""
        subject_str = data.get("subject")
        if not subject_str:
            raise ValueError("Missing 'subject' in WebFinger response")

        subject = Resource.parse(subject_str)

        links_data = data.get("links", [])
        links = [
            Link(
                rel=link_data.get("rel"),
                type=link_data.get("type"),
                href=link_data.get("href"),
            )
            for link_data in links_data
        ]

        return cls(subject=subject, links=links)

    def get(self, link_type: str) -> Union[Link, List[Link], None]:
        """
        Gets links by their 'type' attribute.

        Args:
            link_type: The 'type' of the link to find.

        Returns:
            A single Link object if exactly one is found.
            A list of Link objects if multiple are found.
            None if no matching links are found.
        """
        found_links = [link for link in self.links if link.type == link_type]

        if not found_links:
            return None
        elif len(found_links) == 1:
            return found_links[0]
        else:
            return found_links
