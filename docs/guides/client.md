# Using the Client

The `apkit.client` module provides an asynchronous client for communicating with other ActivityPub servers.

```python
from apkit.client.asyncio import ActivityPubClient

async def main():
    async with ActivityPubClient() as client:
        # Fetch a remote Actor or Object
        actor = await client.actor.fetch("https://example.com/users/someuser")
        if actor:
            print(f"Fetched actor: {actor.name}")

        # Send an activity (requires key configuration for signing)
        # await client.activity.send( ... )
```
