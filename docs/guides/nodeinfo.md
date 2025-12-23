# Nodeinfo

The `apkit.nodeinfo` module provides tools to generate [Nodeinfo](https://nodeinfo.diaspora.software/) documents, which are used to publish standardized metadata about an ActivityPub server. This information helps other servers and services understand the capabilities and statistics of your instance.

`apkit` offers a `NodeinfoBuilder` to simplify the process of creating valid Nodeinfo 2.0 or 2.1 documents.

## Using the NodeinfoBuilder

The builder uses a fluent interface (method chaining) to let you configure the Nodeinfo document step-by-step. Once all the required information is set, you can call the `build()` method to get the final `Nodeinfo` object.

Here is a complete example of how to create a Nodeinfo 2.1 document:

```python
from apkit.nodeinfo.builder import NodeinfoBuilder, Protocol, Inbound, Outbound

# 1. Initialize the builder for a specific version
builder = NodeinfoBuilder(version="2.1")

# 2. Set server software information
builder.set_software(
    name="MyAwesomeServer",
    version="1.2.3",
    repository="https://git.example.com/user/myawesomeserver",
    homepage="https://maws.example.com"
)

# 3. Define supported protocols
builder.set_protocols(["activitypub"])

# 4. Specify inbound and outbound services
builder.set_services(
    inbound=["atom1.0", "rss2.0"],
    outbound=["twitter"]
)

# 5. Set user statistics
builder.set_usage(
    users_total=150,
    active_halfyear=75,
    active_month=40,
    local_posts=5000,
    local_comments=25000
)

# 6. Set registration policy
builder.set_open_registrations(True)

# 7. Add arbitrary metadata
builder.set_metadata({"nodeName": "My Awesome Node"})

# 8. Build the final Nodeinfo object
try:
    nodeinfo = builder.build()
    # The object can be easily converted to a dictionary or JSON
    print(nodeinfo.to_json(indent=2))
except (ValueError, TypeError) as e:
    print(f"Error building Nodeinfo: {e}")

```

Using the Chained Method:
```python
from apkit.nodeinfo.builder import NodeinfoBuilder, Protocol, Inbound, Outbound

# 1. Initialize the builder for a specific version
builder = NodeinfoBuilder(version="2.1")


try:
    nodeinfo = (
        builder
        # 2. Set server software information
        .set_software(
            name="MyAwesomeServer",
            version="1.2.3",
            repository="https://git.example.com/user/myawesomeserver",
            homepage="https://maws.example.com"
        ) 
        # 3. Define supported protocols
        .set_protocols(["activitypub"]) 
        # 4. Specify inbound and outbound services
        .set_services(
            inbound=["atom1.0", "rss2.0"],
            outbound=["twitter"]
        ) 
        # 5. Set user statistics
        .set_usage(
            users_total=150,
            active_halfyear=75,
            active_month=40,
            local_posts=5000,
            local_comments=25000
        ) 
        # 6. Set registration policy
        .set_open_registrations(True)
        # 7. Add arbitrary metadata 
        .set_metadata({"nodeName": "My Awesome Node"})
        # 8. Build the final Nodeinfo object
        .build() 
    )
    # The object can be easily converted to a dictionary or JSON
    print(nodeinfo.to_json(indent=2))
except (ValueError, TypeError) as e:
    print(f"Error building Nodeinfo: {e}")
```

### Builder Methods

- **`__init__(version="2.1")`**: Creates a new builder instance. Accepts `"2.1"` or `"2.0"`.
- **`set_software(...)`**: Sets the server's software details. `name` and `version` are required.
- **`set_protocols(...)`**: Defines the protocols the server supports, like `activitypub`.
- **`set_services(...)`**: Lists the inbound and outbound services the server can connect to.
- **`set_usage(...)`**: Provides user and content statistics. `users_total` is required.
- **`set_open_registrations(...)`**: A boolean indicating if new user registrations are open. This is required.
- **`set_metadata(...)`**: Allows adding arbitrary key-value pairs to the document.
- **`build()`**: Validates the provided data and returns a `Nodeinfo` object. It will raise a `ValueError` or `TypeError` if any required fields are missing or invalid.

### Output

The example above would produce the following JSON output:

```json
{
  "version": "2.1",
  "software": {
    "name": "MyAwesomeServer",
    "version": "1.2.3",
    "repository": "https://git.example.com/user/myawesomeserver",
    "homepage": "https://maws.example.com"
  },
  "protocols": [
    "activitypub"
  ],
  "services": {
    "inbound": [
      "atom1.0",
      "rss2.0"
    ],
    "outbound": [
      "twitter"
    ]
  },
  "openRegistrations": true,
  "usage": {
    "users": {
      "total": 150,
      "activeHalfyear": 75,
      "activeMonth": 40
    },
    "localPosts": 5000,
    "localComments": 25000
  },
  "metadata": {
    "nodeName": "My Awesome Node"
  }
}
```
