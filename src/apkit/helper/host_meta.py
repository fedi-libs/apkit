import json
import xml.etree.ElementTree
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Union

HAS_LXML = False
try:
    from lxml import etree as _lxml

    lxml_etree = _lxml
    HAS_LXML = True
except ImportError:
    pass


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

        if HAS_LXML and lxml_etree is not None:
            return cls._parse_with_lxml(xml_data)
        else:
            return cls._parse_with_std_etree(xml_data)

    @classmethod
    def _parse_with_lxml(cls, xml_data: bytes) -> "HostMeta":
        assert lxml_etree is not None

        ns = {"xrd": "http://docs.oasis-open.org/ns/xri/xrd-1.0"}
        parser = lxml_etree.XMLParser(recover=True, no_network=True)
        root = lxml_etree.fromstring(xml_data, parser=parser)

        nodes = root.xpath("xrd:Link", namespaces=ns)

        links = [
            HostMetaLink(
                rel=str(n.get("rel", "")),
                type=n.get("type"),
                href=n.get("href"),
                template=n.get("template"),
            )
            for n in nodes
        ]
        return cls(links)

    @classmethod
    def _parse_with_std_etree(cls, xml_data: bytes) -> "HostMeta":
        ns = {"xrd": "http://docs.oasis-open.org/ns/xri/xrd-1.0"}
        root = xml.etree.ElementTree.fromstring(xml_data)

        nodes = root.findall("xrd:Link", ns)

        links = [
            HostMetaLink(
                rel=n.get("rel", ""),
                type=n.get("type"),
                href=n.get("href"),
                template=n.get("template"),
            )
            for n in nodes
        ]
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
        if HAS_LXML and lxml_etree is not None:
            return self._to_xml_with_lxml()
        return self._to_xml_with_std_etree()

    def _to_xml_with_lxml(self) -> str:
        if lxml_etree is None:
            raise RuntimeError("lxml is not available even though HAS_LXML is True.")
        nsmap = {None: "http://docs.oasis-open.org/ns/xri/xrd-1.0"}
        root = lxml_etree.Element("XRD", nsmap=nsmap)

        for link in self.links:
            attrs = {k: v for k, v in link._asdict().items() if v is not None}
            lxml_etree.SubElement(root, "Link", attrs)

        return lxml_etree.tostring(
            root, encoding="UTF-8", xml_declaration=True, pretty_print=True
        ).decode("utf-8")

    def _to_xml_with_std_etree(self) -> str:
        xml.etree.ElementTree.register_namespace(
            "", "http://docs.oasis-open.org/ns/xri/xrd-1.0"
        )
        root = xml.etree.ElementTree.Element(
            "{http://docs.oasis-open.org/ns/xri/xrd-1.0}XRD"
        )

        for link in self.links:
            attrs = {k: v for k, v in link._asdict().items() if v is not None}
            xml.etree.ElementTree.SubElement(
                root, "{http://docs.oasis-open.org/ns/xri/xrd-1.0}Link", attrs
            )

        return xml.etree.ElementTree.tostring(root, encoding="unicode")

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
