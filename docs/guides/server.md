# Advanced Server Features

### Handling Various Activities

The `@app.on()` decorator can handle any type of ActivityPub activity, such as `Create`, `Like`, `Announce`, and `Undo`, in addition to `Follow`. By specifying the activity type as an argument, the handler will be executed when that activity is POSTed to the inbox.

```python
from apkit.models import Create, Undo, Like
from apkit.server.types import Context

@app.on(Create)
async def on_create(ctx: Context):
    activity = ctx.activity
    if not isinstance(activity, Create): return
    # Process Create activity
    print(f"Received Create activity: {activity.id}")

@app.on(Undo)
async def on_undo(ctx: Context):
    activity = ctx.activity
    if not isinstance(activity, Undo): return
    # Process Undo activity (e.g., undoing a Like)
    if isinstance(activity.object, Like):
        print(f"Undo Like: {activity.object.id}")
```

### Structuring with `SubRouter`

As your application grows, you can use `SubRouter` to modularize your endpoints, similar to FastAPI's `APIRouter`. `apkit`-specific decorators like `@sub.nodeinfo()` are also available on `SubRouter`.

```python
# in routes/nodeinfo.py
from apkit.server import SubRouter

sub = SubRouter()

@sub.nodeinfo("/ni/2.0", "2.0")
async def nodeinfo_20_endpoint():
    # ...
    pass

# in main.py
from routes.nodeinfo import sub as nodeinfo_router

app.include_router(nodeinfo_router)
```
