import json
from collections import defaultdict
from typing import Any, Dict, List, NamedTuple, Optional, Union

from lxml import etree as etree
from lxml.etree import _Element


class HostMetaLink(NamedTuple):
    rel: str
    type: Optional[str]
    href: Optional[str]
    template: Optional[str]


class HostMeta:
    __slots__ = ("links", "_rel_map")

    def __init__(self, links: List[HostMetaLink]):
        self.links = links
        rel_map: Dict[str, List[HostMetaLink]] = defaultdict(list)
        for link in links:
            rel_map[link.rel].append(link)
        self._rel_map = dict(rel_map)

    @classmethod
    def from_json(cls, json_data: Union[str, bytes]) -> "HostMeta":
        data = json.loads(json_data)
        links_data = data.get("links", [])

        links = [
            HostMetaLink(
                rel=i.get("rel", ""),
                type=i.get("type"),
                href=i.get("href"),
                template=i.get("template"),
            )
            for i in links_data
        ]
        return cls(links)

    @classmethod
    def from_xml(cls, xml_data: Union[str, bytes]) -> "HostMeta":
        if isinstance(xml_data, str):
            xml_data = xml_data.encode("utf-8")

        ns = {"xrd": "http://docs.oasis-open.org/ns/xri/xrd-1.0"}
        parser = etree.XMLParser(recover=True, no_network=True)
        root = etree.fromstring(xml_data, parser=parser)

        result = root.xpath("xrd:Link", namespaces=ns)
        nodes = result if isinstance(result, list) else []

        links: List[HostMetaLink] = []
        for n in nodes:
            if isinstance(n, _Element):
                links.append(
                    HostMetaLink(
                        rel=str(n.get("rel", "")),
                        type=n.get("type"),
                        href=n.get("href"),
                        template=n.get("template"),
                    )
                )
        return cls(links)

    def to_json(self, indent: Optional[int] = None) -> str:
        data = {
            "links": [
                {k: v for k, v in link._asdict().items() if v is not None}
                for link in self.links
            ]
        }
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def to_xml(self) -> str:
        nsmap: dict[Any, str] = {None: "http://docs.oasis-open.org/ns/xri/xrd-1.0"}
        root = etree.Element("XRD", nsmap=nsmap)

        for link in self.links:
            attrs = {k: v for k, v in link._asdict().items() if v is not None}
            etree.SubElement(root, "Link", attrs)

        return etree.tostring(
            root, encoding="UTF-8", xml_declaration=True, pretty_print=True
        ).decode("utf-8")

    def find_link(self, rel: str) -> Optional[HostMetaLink]:
        return next((i for i in self.links if i.rel == rel), None)

    def get(self, rel: str) -> Union[HostMetaLink, List[HostMetaLink], None]:
        found = self._rel_map.get(rel)

        if not found:
            return None

        if len(found) == 1:
            return found[0]

        return found

    def get_all(self, rel: str) -> List[HostMetaLink]:
        return self._rel_map.get(rel, [])

    @property
    def lrdd(self) -> Optional[HostMetaLink]:
        found = self._rel_map.get("lrdd")
        return found[0] if found else None
