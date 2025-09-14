# Configuration

`apkit`'s behavior is configured through the `apkit.config.AppConfig` class. Currently, the main configuration option is `actor_keys`.

You should provide an async function to `actor_keys` that returns the private keys for the actors managed by your server. This function is called whenever `apkit` needs to sign an activity before sending it to another server.

```python
from apkit.config import AppConfig
from apkit.server.types import ActorKey

# This function is responsible for returning the appropriate
# private key based on the request context.
async def get_my_actor_keys(identifier: str) -> list[ActorKey]:
    # ... Logic to fetch keys from a database or elsewhere ...
    if identifier == "user123":
        return [ActorKey(key_id="https://example.com/users/user123#main-key", private_key=...)]
    return []

app_config = AppConfig(
    actor_keys=get_my_actor_keys
)

app = ActivityPubServer(apkit_config=app_config)
```
