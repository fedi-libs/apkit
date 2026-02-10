import pytest
from dataclasses import FrozenInstanceError
from apkit.client.models import Resource, Link, WebfingerResult

@pytest.fixture
def xrd_valid():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Subject>acct:alice@example.com</Subject>
        <Alias>https://example.com/alice</Alias>
        <Link href="https://example.com/alice" rel="http://webfinger.net/rel/profile-page" type="text/html" />
        <Link href="https://example.com/alice" rel="self" type="application/activity+json" />
        <Link rel="http://ostatus.org/schema/1.0/subscribe" template="https://example.com/ostatus_subscribe?acct={uri}" />
    </XRD>"""

@pytest.fixture
def xrd_invalid():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link rel="self" href="https://example.com/user" />
    </XRD>"""

class TestResource:
    """Test cases for the Resource class."""

    def test_resource_creation(self):
        """Test basic Resource creation."""
        resource = Resource(username="alice", host="example.com", url=None)
        assert resource.username == "alice"
        assert resource.host == "example.com"
        assert resource.url is None

    def test_resource_creation_with_url(self):
        """Test Resource creation with URL."""
        resource = Resource(username="", host="", url="https://example.com")
        assert resource.username == ""
        assert resource.host == ""
        assert resource.url == "https://example.com"

    def test_resource_string_representation(self):
        """Test the string representation of Resource."""
        resource = Resource(username="bob", host="example.org", url=None)
        assert str(resource) == "acct:bob@example.org"

    def test_resource_export(self):
        """Test the export method."""
        resource = Resource(username="charlie", host="example.net", url=None)
        assert resource.export() == "acct:charlie@example.net"

    def test_parse_valid_resource_string(self):
        """Test parsing valid resource strings."""
        # Test with acct: prefix
        resource = Resource.parse("acct:user@example.com")
        assert resource.username == "user"
        assert resource.host == "example.com"
        assert resource.url is None

        # Test without acct: prefix
        resource = Resource.parse("user@example.com")
        assert resource.username == "user"
        assert resource.host == "example.com"
        assert resource.url is None

    def test_parse_invalid_resource_string(self):
        """Test parsing invalid resource strings."""
        # Test with URL-like string
        resource = Resource.parse("https://example.com/profile")
        assert resource.username == ""
        assert resource.host == ""
        assert resource.url == "https://example.com/profile"

        # Test malformed string
        resource = Resource.parse("invalid@string@format")
        assert resource.username == ""
        assert resource.host == ""
        assert resource.url == "invalid@string@format"

    def test_resource_immutability(self):
        """Test that Resource is immutable (frozen dataclass)."""
        resource = Resource(username="alice", host="example.com", url=None)
        with pytest.raises(AttributeError):
            resource.username = "eve" # pyrefly: ignore


class TestLink:
    """Test cases for the Link class."""

    def test_link_creation(self):
        """Test basic Link creation."""
        link = Link(rel="profile", type="text/html", href="https://example.com/profile")
        assert link.rel == "profile"
        assert link.type == "text/html"
        assert link.href == "https://example.com/profile"

    def test_link_creation_with_none_values(self):
        """Test Link creation with None values."""
        link = Link(rel="self", type=None, href=None)
        assert link.rel == "self"
        assert link.type is None
        assert link.href is None

    def test_link_to_json(self):
        """Test the to_json method."""
        link = Link(rel="profile", type="text/html", href="https://example.com/profile")
        expected = {
            "rel": "profile",
            "type": "text/html",
            "href": "https://example.com/profile",
        }
        assert link.to_json() == expected

    def test_link_to_json_with_none_values(self):
        """Test to_json method with None values."""
        link = Link(rel="self", type=None, href=None)
        expected = {"rel": "self", "type": None, "href": None}
        assert link.to_json() == expected

    def test_link_immutability(self):
        """Test that Link is immutable (frozen dataclass)."""
        link = Link(rel="profile", type="text/html", href="https://example.com/profile")
        with pytest.raises(AttributeError):
            link.rel = "self" # pyrefly: ignore


class TestWebfingerResult:
    """Test cases for the WebfingerResult class."""

    def test_webfinger_result_creation(self):
        """Test basic WebfingerResult creation."""
        subject = Resource(username="alice", host="example.com", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.com/alice"),
            Link(
                rel="self",
                type="application/activity+json",
                href="https://example.com/users/alice",
            ),
        ]
        result = WebfingerResult(subject=subject, links=links)

        assert result.subject == subject
        assert result.links == links

    def test_webfinger_result_to_json(self):
        """Test the to_json method."""
        subject = Resource(username="bob", host="example.org", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.org/bob"),
            Link(
                rel="self",
                type="application/activity+json",
                href="https://example.org/users/bob",
            ),
        ]
        result = WebfingerResult(subject=subject, links=links)

        expected = {
            "subject": "acct:bob@example.org",
            "links": [
                {
                    "rel": "profile",
                    "type": "text/html",
                    "href": "https://example.org/bob",
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": "https://example.org/users/bob",
                },
            ],
        }
        assert result.to_json() == expected

    def test_webfinger_result_from_dict(self):
        """Test creating WebfingerResult from dictionary."""
        data = {
            "subject": "acct:charlie@example.net",
            "links": [
                {
                    "rel": "profile",
                    "type": "text/html",
                    "href": "https://example.net/charlie",
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": "https://example.net/users/charlie",
                },
            ],
        }

        result = WebfingerResult.from_dict(data)

        assert result.subject.username == "charlie"
        assert result.subject.host == "example.net"
        assert len(result.links) == 2
        assert result.links[0].rel == "profile"
        assert result.links[1].rel == "self"

    def test_webfinger_result_from_dict_missing_subject(self):
        """Test from_dict with missing subject raises ValueError."""
        data = {
            "links": [
                {
                    "rel": "profile",
                    "type": "text/html",
                    "href": "https://example.com/profile",
                }
            ]
        }

        with pytest.raises(ValueError, match="Missing 'subject' in WebFinger response"):
            WebfingerResult.from_dict(data)

    def test_webfinger_result_from_dict_empty_links(self):
        """Test from_dict with empty links list."""
        data = {"subject": "acct:user@example.com", "links": []}

        result = WebfingerResult.from_dict(data)
        assert result.subject.username == "user"
        assert result.subject.host == "example.com"
        assert result.links == []

    def test_webfinger_result_get_single_link(self):
        """Test get method with single matching link."""
        subject = Resource(username="alice", host="example.com", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.com/alice"),
            Link(
                rel="self",
                type="application/activity+json",
                href="https://example.com/users/alice",
            ),
        ]
        result = WebfingerResult(subject=subject, links=links)

        link = result.get("text/html")
        assert isinstance(link, Link)
        assert link.type == "text/html"
        assert link.rel == "profile"

    def test_webfinger_result_get_multiple_links(self):
        """Test get method with multiple matching links."""
        subject = Resource(username="alice", host="example.com", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.com/alice"),
            Link(
                rel="alternate", type="text/html", href="https://example.com/alt/alice"
            ),
            Link(
                rel="self",
                type="application/activity+json",
                href="https://example.com/users/alice",
            ),
        ]
        result = WebfingerResult(subject=subject, links=links)

        found_links = result.get("text/html")
        assert isinstance(found_links, list)
        assert len(found_links) == 2
        assert all(link.type == "text/html" for link in found_links)

    def test_webfinger_result_get_no_links(self):
        """Test get method with no matching links."""
        subject = Resource(username="alice", host="example.com", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.com/alice"),
            Link(
                rel="self",
                type="application/activity+json",
                href="https://example.com/users/alice",
            ),
        ]
        result = WebfingerResult(subject=subject, links=links)

        link = result.get("application/xml")
        assert link is None

    def test_webfinger_result_immutability(self):
        """Test that WebfingerResult is immutable (frozen dataclass)."""
        subject = Resource(username="alice", host="example.com", url=None)
        links = [
            Link(rel="profile", type="text/html", href="https://example.com/alice")
        ]
        result = WebfingerResult(subject=subject, links=links)

        with pytest.raises(AttributeError):
            result.subject = Resource(username="bob", host="example.com", url=None) # pyrefly: ignore

    def test_webfinger_result_from_xml(self, xrd_valid):
        """Test creating WebfingerResult from XML (XRD)."""
        result = WebfingerResult.from_xml(xrd_valid)

        assert result.subject.username == "alice"
        assert result.subject.host == "example.com"
        assert len(result.links) == 3

        ap_link = result.get("application/activity+json")
        assert isinstance(ap_link, Link)
        assert ap_link.href == "https://example.com/alice"

        sub_links = [l for l in result.links if "subscribe" in l.rel]
        assert len(sub_links) == 1
        assert sub_links[0].href == "https://example.com/ostatus_subscribe?acct={uri}"

    def test_webfinger_result_from_xml_missing_subject(self, xrd_invalid):
        """Test from_xml with missing subject raises ValueError."""
        with pytest.raises(ValueError, match="Missing 'Subject'"):
            WebfingerResult.from_xml(xrd_invalid)

    def test_webfinger_result_from_xml_bytes(self, xrd_valid):
        """Test from_xml with bytes input (common in HTTP responses)."""
        result = WebfingerResult.from_xml(xrd_valid.encode("utf-8"))
        assert result.subject.username == "alice"

    def test_webfinger_result_immutability(self):
        """Test that WebfingerResult is immutable (__slots__ protection)."""
        subject = Resource(username="alice", host="example.com", url=None)
        result = WebfingerResult(subject=subject, links=[])

        with pytest.raises(AttributeError):
            result.subject = Resource(username="bob", host="example.com", url=None) # type: ignore

    def test_webfinger_result_get_consistency(self, xrd_valid):
        """Test that get() returns correct types regardless of parse source."""
        result = WebfingerResult.from_xml(xrd_valid)

        found = result.get("application/activity+json")
        assert isinstance(found, Link)

        assert result.get("image/png") is None

    def test_xml_output_roundtrip(self):
        result = WebfingerResult.from_dict({"subject": "acct:alice@example.com", "links": []})
        xml_data = result.to_xml()
        reparsed = WebfingerResult.from_xml(xml_data)
        assert str(reparsed.subject) == str(result.subject)

def test_integration():
    """Integration test covering the full workflow."""
    # Parse a resource string
    resource_str = "acct:testuser@example.org"
    resource = Resource.parse(resource_str)

    # Create links
    links = [
        Link(
            rel="self",
            type="application/activity+json",
            href="https://example.org/users/testuser",
        ),
        Link(rel="profile", type="text/html", href="https://example.org/@testuser"),
        Link(
            rel="http://webfinger.net/rel/profile-page",
            type="text/html",
            href="https://example.org/@testuser",
        ),
    ]

    # Create WebfingerResult
    result = WebfingerResult(subject=resource, links=links)

    # Convert to JSON
    json_data = result.to_json()

    # Parse back from dictionary
    reconstructed = WebfingerResult.from_dict(json_data)

    # Verify round-trip
    assert reconstructed.subject.username == "testuser"
    assert reconstructed.subject.host == "example.org"
    assert len(reconstructed.links) == 3

    # Test getting specific links
    activity_json_link = reconstructed.get("application/activity+json")
    assert isinstance(activity_json_link, Link)
    assert activity_json_link is not None
    assert activity_json_link.rel == "self"

    html_links = reconstructed.get("text/html")
    assert isinstance(html_links, list)
    assert len(html_links) == 2

def test_full_roundtrip_integration(xrd_valid):
    from_xml = WebfingerResult.from_xml(xrd_valid)
    json_data = from_xml.to_json()
    reconstructed = WebfingerResult.from_dict(json_data)

    assert str(reconstructed.subject) == str(from_xml.subject)
    assert len(reconstructed.links) == len(from_xml.links)

    def get_first_href(result: WebfingerResult, l_type: str) -> str:
        res = result.get(l_type)
        if isinstance(res, list):
            return res[0].href or ""
        if res is not None:
            return res.href or ""
        return ""

    assert get_first_href(reconstructed, "text/html") == get_first_href(from_xml, "text/html")
    assert get_first_href(reconstructed, "application/activity+json") == get_first_href(from_xml, "application/activity+json")
