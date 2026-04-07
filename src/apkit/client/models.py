import re as standard_re
from collections import defaultdict
from typing import (
    Any,
    Dict,
    List,
    Optional,
    ParamSpec,
    TypeVar,
    Union,
    cast,
)

try:
    import re2 as re  #
except ImportError:
    re = standard_re  # ty: ignore[invalid-assignment]

try:
    import lxml.etree as lxml_etree

    HAS_LXML = True
except ImportError:
    lxml_etree = None  # ty: ignore[invalid-assignment]
    HAS_LXML = False

from xml.etree import ElementTree as std_etree  # noqa: N813

P = ParamSpec("P")
R = TypeVar("R")

_ACCT_RE = re.compile(r"^([^@]+)@([^@]+)$")


class Resource:
    """Represents a WebFinger resource."""

    __slots__ = ("_username", "_host", "_url")

    def __init__(self, username: str, host: str, url: Optional[str] = None):
        self._username = username
        self._host = host
        self._url = url

    def __str__(self) -> str:
        return f"acct:{self._username}@{self._host}"

    @property
    def username(self) -> str:
        return self._username

    @property
    def host(self) -> str:
        return self._host

    @property
    def url(self) -> Optional[str]:
        return self._url

    @classmethod
    def parse(cls, resource_str: str) -> "Resource":
        orig = resource_str
        if resource_str.startswith("acct:"):
            resource_str = resource_str[5:]

        if "@" in resource_str:
            parts = resource_str.split("@")
            if len(parts) == 2:
                return cls(username=parts[0], host=parts[1], url=None)

        match = _ACCT_RE.match(resource_str)
        if not match:
            return cls(username="", host="", url=orig)

        u, h = match.groups()
        if isinstance(u, str) and isinstance(h, str):
            return cls(username=u, host=h, url=None)

        return cls(username=str(u or ""), host=str(h or ""), url=None)

    def export(self) -> str:
        return f"acct:{self._username}@{self._host}"


class Link:
    """Represents a link in a WebFinger response."""

    __slots__ = ("_rel", "_type", "_href")

    def __init__(self, rel: str, type: Optional[str], href: Optional[str]):
        self._rel = rel
        self._type = type
        self._href = href

    @property
    def rel(self) -> str:
        return self._rel

    @property
    def type(self) -> Optional[str]:
        return self._type

    @property
    def href(self) -> Optional[str]:
        return self._href

    def to_json(self) -> dict:
        return {"rel": self._rel, "type": self._type, "href": self._href}


class WebfingerResult:
    __slots__ = ("_subject", "_links", "_type_map")

    def __init__(
        self,
        subject: Resource,
        links: List[Link],
    ):
        self._subject = subject
        self._links = links

        type_map = defaultdict(list)
        for item in links:
            l_type = item.type
            if l_type:
                type_map[l_type].append(item)

        self._type_map: Dict[str, List[Link]] = dict(type_map)

    @property
    def subject(self) -> Resource:
        return self._subject

    @property
    def links(self) -> List[Link]:
        return self._links

    def to_json(self) -> dict:
        return {
            "subject": self._subject.export(),
            "links": [link.to_json() for link in self._links],
        }

    def to_xml(self, encoding: str = "UTF-8") -> bytes:
        ns = "http://docs.oasis-open.org/ns/xri/xrd-1.0"

        if HAS_LXML and lxml_etree is not None:
            root = lxml_etree.Element(f"{{{ns}}}XRD", nsmap=cast(dict, {None: ns}))
            subject = lxml_etree.SubElement(root, f"{{{ns}}}Subject")
            subject.text = self._subject.export()

            for link in self._links:
                l_elem = lxml_etree.SubElement(root, f"{{{ns}}}Link")
                if link.rel:
                    l_elem.set("rel", link.rel)
                if link.type:
                    l_elem.set("type", link.type)
                if link.href:
                    l_elem.set("href", link.href)

            r = lxml_etree.tostring(
                root, encoding=encoding, xml_declaration=True, pretty_print=True
            )
            return r if isinstance(r, bytes) else r.encode("utf-8")
        else:
            std_etree.register_namespace("", ns)
            root = std_etree.Element(f"{{{ns}}}XRD")

            subject = std_etree.SubElement(root, f"{{{ns}}}Subject")
            subject.text = self._subject.export()

            for link in self._links:
                l_elem = std_etree.SubElement(root, f"{{{ns}}}Link")
                if link.rel:
                    l_elem.set("rel", link.rel)
                if link.type:
                    l_elem.set("type", link.type)
                if link.href:
                    l_elem.set("href", link.href)

            return std_etree.tostring(root, encoding=encoding, xml_declaration=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebfingerResult":
        subject_str = data.get("subject")
        if not subject_str:
            raise ValueError("Missing 'subject' in WebFinger response")

        links_data = data.get("links", [])
        links = []

        append_link = links.append

        for item in links_data:
            link = Link(
                rel=str(item.get("rel", "")),
                type=item.get("type"),
                href=item.get("href"),
            )
            append_link(link)

        return cls(Resource.parse(subject_str), links)

    @classmethod
    def from_xml(cls, xml_data: Union[str, bytes]) -> "WebfingerResult":
        """Parses an XRD (XML) string/bytes into a WebfingerResult."""
        if isinstance(xml_data, str):
            xml_data = xml_data.encode("utf-8")

        ns = {"xrd": "http://docs.oasis-open.org/ns/xri/xrd-1.0"}

        if HAS_LXML and lxml_etree is not None:
            parser = lxml_etree.XMLParser(recover=True, no_network=True)
            root = lxml_etree.fromstring(xml_data, parser=parser)

            subject_nodes = root.xpath("xrd:Subject/text()", namespaces=ns)
            if isinstance(subject_nodes, list) and subject_nodes:
                subject_str = str(subject_nodes[0])
            else:
                subject_str = ""
        else:
            root = std_etree.fromstring(xml_data)
            subject_node = root.find("xrd:Subject", ns)
            subject_str = (subject_node.text if subject_node is not None else "") or ""
        xpath_result = root.findall("xrd:Link", ns)
        if not isinstance(xpath_result, list):
            link_nodes: List[Any] = []
        else:
            link_nodes = xpath_result

        if not subject_str:
            raise ValueError("Missing 'Subject' in XRD response")

        links: List[Link] = []
        for node in link_nodes:
            if hasattr(node, "get"):
                rel = str(node.get("rel", ""))
                l_type = node.get("type")
                href = node.get("href") or node.get("template")
                links.append(Link(rel=rel, type=l_type, href=href))

        return cls(Resource.parse(subject_str), links)

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
        found = self._type_map.get(link_type)
        if found is None:
            return None
        return found[0] if len(found) == 1 else found
