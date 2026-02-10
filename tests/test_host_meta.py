import json

import pytest
from apkit.helper.host_meta import HostMeta, HostMetaLink, HAS_LXML

VALID_XRD = """<?xml version="1.0" encoding="UTF-8"?>
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
    <Link rel="lrdd" type="application/xrd+xml" template="https://example.com/.well-known/webfinger?resource={uri}"/>
    <Link rel="http://spec.example.net/rel/1" href="https://example.com/1"/>
    <Link rel="http://spec.example.net/rel/1" href="https://example.com/2"/>
</XRD>
"""

VALID_JRD = """
{
  "links": [
    {
      "rel": "lrdd",
      "type": "application/jrd+json",
      "template": "https://example.com/.well-known/webfinger?resource={uri}"
    }
  ]
}
"""

@pytest.fixture
def host_meta():
    return HostMeta.from_xml(VALID_XRD)

class TestHostMeta:
    def test_from_xml_basic(self, host_meta: HostMeta):
        assert len(host_meta.links) == 3
        assert host_meta.links[0].rel == "lrdd"

    def test_get_single(self, host_meta: HostMeta):
        link = host_meta.get("lrdd")
        assert isinstance(link, HostMetaLink)
        assert link.template == "https://example.com/.well-known/webfinger?resource={uri}"

    def test_get_multiple(self, host_meta: HostMeta):
        links = host_meta.get("http://spec.example.net/rel/1")
        assert isinstance(links, list)
        assert len(links) == 2
        assert links[0].href == "https://example.com/1"
        assert links[1].href == "https://example.com/2"

    def test_get_none(self, host_meta: HostMeta):
        assert host_meta.get("undefined") is None

    def test_get_all(self, host_meta: HostMeta):
        assert len(host_meta.get_all("lrdd")) == 1
        assert len(host_meta.get_all("http://spec.example.net/rel/1")) == 2
        assert host_meta.get_all("undefined") == []

    def test_find_link(self, host_meta: HostMeta):
        link = host_meta.find_link("http://spec.example.net/rel/1")
        assert link is not None
        assert link.href == "https://example.com/1"

    @pytest.mark.parametrize("parser_method", [
        "_parse_with_std_etree",
        pytest.param("_parse_with_lxml", marks=pytest.mark.skipif(not HAS_LXML, reason="lxml not installed"))
    ])
    def test_parsers_directly(self, parser_method):
        method = getattr(HostMeta, parser_method)
        instance = method(VALID_XRD.encode("utf-8"))
        assert len(instance.links) == 3
        assert instance.links[0].rel == "lrdd"

    def test_malformed_xml(self):
        bad_xml = "<XRD><Link></XRD>"
        with pytest.raises(Exception):
            HostMeta._parse_with_std_etree(bad_xml.encode("utf-8"))

    def test_from_json_basic(self):
        hm = HostMeta.from_json(VALID_JRD)
        assert len(hm.links) == 1

        link = hm.get("lrdd")
        assert isinstance(link, HostMetaLink)
        assert link.rel == "lrdd"
        assert link.template == "https://example.com/.well-known/webfinger?resource={uri}"
        assert link.type == "application/jrd+json"

    def test_from_json_empty_links(self):
        empty_jrd = '{"links": []}'
        hm = HostMeta.from_json(empty_jrd)
        assert hm.links == []
        assert hm.get("lrdd") is None

    def test_compatibility(self):
        xml_data = """<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
            <Link rel="lrdd" template="https://example.com/?q={uri}"/>
        </XRD>"""

        hm_xml = HostMeta.from_xml(xml_data)
        hm_json = HostMeta.from_json(VALID_JRD)

        assert type(hm_xml.links[0]) is type(hm_json.links[0])
        assert isinstance(hm_xml.links[0], HostMetaLink)

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            HostMeta.from_json("{ invalid json }")

    def test_to_json(self, host_meta: HostMeta):
        json_str = host_meta.to_json()
        new_meta = HostMeta.from_json(json_str)
        
        assert len(new_meta.links) == len(host_meta.links)
        assert new_meta.links[0].rel == host_meta.links[0].rel
        assert "links" in json.loads(json_str)

    @pytest.mark.parametrize("use_lxml", [
        pytest.param(True, marks=pytest.mark.skipif(not HAS_LXML, reason="lxml missing")),
        False
    ])
    def test_to_xml_roundtrip(self, host_meta: HostMeta, use_lxml):
        if use_lxml:
            xml_str = host_meta._to_xml_with_lxml()
        else:
            xml_str = host_meta._to_xml_with_std_etree()
            
        new_meta = HostMeta.from_xml(xml_str)
        new_lrdd = new_meta.find_link("lrdd")
        orig_lrdd = host_meta.find_link("lrdd")
        
        assert new_lrdd is not None
        assert orig_lrdd is not None
        assert new_lrdd.template == orig_lrdd.template
        assert len(new_meta.links) == len(host_meta.links)

    def test_to_json_excludes_none(self):
        link = HostMetaLink(rel="test", type=None, href="http://ex.com", template=None)
        hm = HostMeta([link])
        data = json.loads(hm.to_json())
        
        assert "rel" in data["links"][0]
        assert "type" not in data["links"][0]
        assert "template" not in data["links"][0]
        
    def test_get_single_link(self, host_meta: HostMeta):
        link = host_meta.get("lrdd")
        
        assert isinstance(link, HostMetaLink)
        assert link.template is not None