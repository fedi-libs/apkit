import re
import pytest
import respx
from aioresponses import aioresponses
from httpx import Response
from apkit.client import ActivityPubClient 

@pytest.fixture(scope="session")
def shared_data():
    data = {
        "actor_head": {
            "Content-Type": "application/activity+json",
            "vary": "Accept-Encoding, Accept"
        },
        "actor_json": {
            "@context": ["https://www.w3.org/ns/activitystreams"],
            "id": "https://example.com/actor",
            "type": "Application",
            "preferredUsername": "actor",
            "inbox": "https://example.com/actor/inbox"
        }
    }
    return data

@respx.mock
def test_get_sync_success(shared_data):
    url = "https://example.com/actor"
    respx.get(url).mock(return_value=Response(
        200, 
        json=shared_data["actor_json"], 
        headers=shared_data["actor_head"]
    ))
    
    with ActivityPubClient() as client:
        with client.get(url) as resp:
            data = resp.json()
            assert data["type"] == "Application"
            assert resp.status == 200

@respx.mock
def test_sync_reused_error():
    url = "https://example.com"
    respx.get(url).mock(return_value=Response(200))
    with ActivityPubClient() as client:
        req = client.get(url)
        with req:
            pass
        with pytest.raises(RuntimeError, match="instance cannot be reused"):
            with req:
                pass

@pytest.mark.asyncio
async def test_get_async_success(shared_data):
    url = "https://example.com/actor"
    with aioresponses() as m:
        m.get(
            url, 
            payload=shared_data["actor_json"], 
            headers=shared_data["actor_head"], 
            status=200
        )
        
        async with ActivityPubClient() as client:
            async with client.get(url) as resp:
                data = await resp.json()
                assert data["type"] == "Application"
                assert resp.status == 200

@pytest.mark.asyncio
async def test_async_uninitialized_error():
    client = ActivityPubClient()
    expected_msg = re.escape("The async client session is not initialized or has been closed. Ensure you are using 'async with ActivityPubClient()'.")
    with pytest.raises(RuntimeError, match=expected_msg):
        async with client.get("https://example.com"):
            pass