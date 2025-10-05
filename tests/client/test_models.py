import pytest
from dataclasses import FrozenInstanceError
from apkit.client.models import Resource, Link, WebfingerResult


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
        with pytest.raises(FrozenInstanceError):
            resource.username = "eve"


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
        with pytest.raises(FrozenInstanceError):
            link.rel = "self"


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

        with pytest.raises(FrozenInstanceError):
            result.subject = Resource(username="bob", host="example.com", url=None)


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
    assert activity_json_link is not None
    assert activity_json_link.rel == "self"

    html_links = reconstructed.get("text/html")
    assert isinstance(html_links, list)
    assert len(html_links) == 2
