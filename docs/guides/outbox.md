# Using Outbox

[Outbox](https://www.w3.org/wiki/ActivityPub/Primer/Outbox) is **required** by the specification, but most implementations recognize an Actor even if it doesn't have an Outbox.

This guide explains how to implement a simple Outbox.

## Define Empty Outbox

First, you must define the Outbox in order to use it:

```python
app.outbox("/users/{identifier}/outbox")
```

The Outbox becomes usable by subscribing to the special Outbox class imported via `from apkit.types import Outbox` using `app.on`:

```python
from apkit.models import OrderedCollection, Person
from apkit.server.types import Context
from apkit.server.responses import ActivityResponse

...

person = Person(
    ...
    outbox="https://example.com/users/1/outbox"
)

@app.on(Outbox)
async def listen_outbox(ctx: Context):
    identifier = ctx.request.path_params.get("identifier")
    col = OrderedCollection(
        id=f"https://example.com/users/{identifier}/outbox",
        total_items=0,
        ordered_items=[]
    )
    return ActivityResponse(col)
```

## Returning real data
In most cases, you don't actually need to return the contents. (However, some implementations use the contents of the outbox to count the number of posts.)

However, this time let us retrieve and return actual data.

```python
from datetime import datetime

from apkit.models import Announce, Create, Delete, Note, Tombstone, Person, OrderedCollection, OrderedCollectionPage
from fastapi.responses import JSONResponse

...

PAGE_SIZE = 20
posts = [
    Announce(
        id="https://example.com/users/alice/activities/4",
        actor=person.id,
        published=datetime(2026, 1, 3),
        to=["https://www.w3.org/ns/activitystreams#Public"],
        object="https://example.net/users/bob/notes/2",
    ),
    Delete(
        id="https://example.com/users/alice/activities/3",
        actor=person.id,
        published=datetime(2026, 1, 2),
        to=["https://www.w3.org/ns/activitystreams#Public"],
        object=Tombstone(
            id="https://example.com/users/alice/notes/2",
        ),
    ),
    Create(
        id="https://example.com/users/alice/activities/1",
        actor=person.id,
        published=datetime(2026, 1, 1),
        to=["https://www.w3.org/ns/activitystreams#Public"],
        object=Note(
            id="https://example.com/users/alice/notes/1",
            attributedTo="https://example.com/users/alice",
            content="<p>Hello World!</p>",
            published=datetime(2026, 1, 1),
            to=["https://www.w3.org/ns/activitystreams#Public"]
        ),
    )
]

@app.on(Outbox)
async def listen_outbox(ctx: Context):
    identifier = ctx.request.path_params.get("identifier")
    if identifier != "alice":
        return JSONResponse({"message": "Not Found"}, status_code=404)
    outbox_url = f"https://example.com/users/{identifier}/outbox"
    
    is_page = ctx.request.query_params.get("page") == "true"
    max_id = ctx.request.query_params.get("max_id")

    if not is_page:
        col = OrderedCollection(
            id=outbox_url,
            total_items=len(posts),
            first=f"{outbox_url}?page=true",
            last=f"{outbox_url}?page=true&min_id={posts[-1].id}" if posts else None
        )
        return ActivityResponse(col)

    start_index = 0
    if max_id:
        for i, p in enumerate(posts):
            if p.id == max_id:
                start_index = i + 1
                break

    page_items = posts[start_index : start_index + PAGE_SIZE]
    
    next_url = None
    if start_index + PAGE_SIZE < len(posts):
        last_item_id = page_items[-1].id
        next_url = f"{outbox_url}?page=true&max_id={last_item_id}"

    page = OrderedCollectionPage(
        id=f"{outbox_url}?page=true" + (f"&max_id={max_id}" if max_id else ""),
        part_of=outbox_url,
        ordered_items=page_items,
        next=next_url
    )
    return ActivityResponse(page)

```

!!! tips "What is `Tombstone`?"

    The `Tombstone` type indicates content that existed in the past but has now been deleted. By returning this object instead of completely removing the item from the Outbox, you can explicitly communicate to the remote server that "this post has been deleted."