# Framework Integration

`apkit` is designed to be framework-agnostic, allowing integration with any Python web framework. This guide explains how to create your own integration, using [`apkit-flask`](https://github.com/fedi-libs/apkit-flask) as a reference.

The core idea is to create a bridge between your web framework's request/response objects and `apkit`'s handlers and context.

## Key Components

A typical integration consists of four main parts:

1.  **Integration Class**: A central class that inherits from `apkit.abc.server.AbstractApkitIntegration` and manages the connection between your app and `apkit`.
2.  **Decorators**: User-friendly decorators (like `@ap.on()`, `@ap.webfinger()`) that register handler functions for different ActivityPub events and endpoints.
3.  **Routing**: Logic that maps incoming web requests from your framework to the appropriate `apkit` handlers.
4.  **Context Object**: A data class inheriting from `apkit.abc.types.AbstractContext` that provides handlers with access to the request, activity data, and helper methods.

---

## Step 1: Create the Integration Class

First, create a class that inherits from `AbstractApkitIntegration`. Its constructor should accept the web framework's application instance and an `apkit.config.AppConfig` object.

This class will store the registered event handlers.

```python
# src/apkit_yourframework/__init__.py
from typing import (
    Any,
    Callable,
    Optional,
    Dict,
)
from apkit.abc.server import AbstractApkitIntegration
from apkit.config import AppConfig
from apkit.models import Activity

# Replace YourFrameworkApp with your framework's app type (e.g., Flask, FastAPI)
from your_framework import YourFrameworkApp

class ApkitIntegration(AbstractApkitIntegration):
    def __init__(self, app: YourFrameworkApp, config: AppConfig = AppConfig()):
        self._app = app
        self._config = config

        # Dictionary to store handlers for activities like Create, Follow, etc.
        self._events: Dict[type[Activity], Callable] = {}
        # Variable to store the outbox handler
        self._outbox: Optional[Callable] = None
        # Variable to store the webfinger handler
        self._webfinger: Optional[Callable] = None

    # ...decorators and methods will be added here...
```

## Step 2: Implement Handler Registration Decorators

Create decorators to allow users to register their functions as handlers for various ActivityPub logic. These decorators simply store the provided function in the integration class.

```python
# In your ApkitIntegration class...

def on(self, activity_type: type[Activity]):
    """Decorator to register a handler for a specific Activity type."""
    def decorator(func: Callable) -> Callable:
        self._events[activity_type] = func
        return func
    return decorator

def outbox(self, func: Callable):
    """Decorator to register the outbox handler."""
    self._outbox = func
    return func

def webfinger(self, func: Callable):
    """Decorator to register the webfinger handler."""
    self._webfinger = func
    return func
```

## Step 3: Set Up Routing

You need to bridge your framework's routing mechanism with the handlers registered in your integration class. This typically involves creating internal route functions that are called by the framework when a request comes in.

An `initialize()` method is a good pattern to set up all the necessary routes at once.

```python
# In your ApkitIntegration class...

from .routes import create_inbox_route, create_webfinger_route

def initialize(self):
    """
    Registers the ActivityPub routes with the web framework.
    """
    # The internal function that will handle inbox requests
    inbox_view = create_inbox_route(self, self._config, self._events)

    # The internal function for webfinger
    webfinger_view = create_webfinger_route(self)

    # Use your framework's method to add URL rules
    self._app.add_url_rule(
        "/inbox",
        view_func=inbox_view,
        methods=["POST"]
    )
    self._app.add_url_rule(
        "/.well-known/webfinger",
        view_func=webfinger_view,
        methods=["GET"]
    )
    # Add other routes like outbox, nodeinfo, etc.
```

The view functions (`create_inbox_route`, etc.) will contain the logic to parse the request, verify signatures (for inbox), and call the appropriate user-registered handler.

Here is a simplified example for an inbox route:

```python
# src/apkit_yourframework/routes/inbox.py
import json
from your_framework import Request, Response, jsonify
from apkit.helper.inbox import InboxVerifier
import apmodel

def create_inbox_route(apkit_integration, config, routes):
    def on_inbox_internal(request: Request) -> Response:
        verifier = InboxVerifier(config)
        body = request.get_data()

        # Verify the HTTP Signature
        if not verifier.verify(body, str(request.url), request.method, dict(request.headers)):
            return jsonify({"message": "Signature Verification Failed"}), 401

        activity = apmodel.load(json.loads(body))

        # Find the registered handler for this activity type
        handler = routes.get(type(activity))
        if handler:
            # Create a context object and call the handler
            ctx = Context(_apkit=apkit_integration, request=request, activity=activity)
            return handler(ctx)

        return jsonify({"message": "Ok"}), 200

    return on_inbox_internal
```

## Step 4: Create the Context Class

The `Context` class provides a clean API for handlers to interact with the request and `apkit`'s features. It inherits from `AbstractContext` and should be tailored to your framework.

```python
# src/apkit_yourframework/types.py
from dataclasses import dataclass
from apkit.abc.types import AbstractContext
from apkit.models import Activity
from your_framework import Request

# Forward-reference your integration class
if TYPE_CHECKING:
    from . import ApkitIntegration

@dataclass
class Context(AbstractContext):
    _apkit: "ApkitIntegration"
    activity: Activity
    request: Request

    def send(self, ...):
        # Implement logic to send activities using apkit's client
        pass

    def get_actor_keys(self, ...):
        # Implement logic to retrieve actor keys
        pass
```

By following these steps, you can create a robust integration for any web framework, providing users with a seamless way to build ActivityPub services. For a complete, real-world example, please refer to the **[`apkit-flask`](https://github.com/fedi-libs/apkit-flask)** repository.
