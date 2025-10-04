from apkit.client.models import Resource
from apkit.client._common import build_webfinger_url


def test_build_webfinger_url():
    host = "example.com"
    resource = Resource(username="alice", host="example.com", url=None)

    url = build_webfinger_url(host, resource)

    assert (
        url
        == "https://example.com/.well-known/webfinger?resource=acct:alice@example.com"
    )
