# Key-Value Storage

`apkit.kv` provides an abstraction layer for a simple key-value store. By default, an in-memory store is used, but you can also use Redis as a backend by installing the `redis` extra.

This can be used for various purposes, such as caching or storing temporary data.

```python
from apkit.kv.inmemory import InMemoryKV

kv = InMemoryKV()

await kv.set("my_key", {"data": "some_value"})
value = await kv.get("my_key")
```
