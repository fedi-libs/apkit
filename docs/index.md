<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
  <a href="https://fedi-libs.github.io/apkit">
    <img src="https://raw.githubusercontent.com/fedi-libs/assets/refs/heads/main/png/apkit.png" alt="apkit" />
  </a>
</p>
<p align="center">
    <em>Powerful Toolkit for ActivityPub Implementations.</em>
</p>
<p align="center">
<a href="https://github.com/fedi-libs/apkit/actions/workflows/publish.yml" target="_blank">
    <img src="https://github.com/fedi-libs/apkit/actions/workflows/publish.yml/badge.svg" alt="Test">
</a>
<a href="https://pypi.org/project/apkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/apkit.svg" alt="Package version">
</a>
<a href="https://pypi.org/project/apkit" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/apkit.svg" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: <a href="https://fedi-libs.github.io/apkit" target="_blank">https://fedi-libs.github.io/apkit</a>

**Source Code**: <a href="https://github.com/fedi-libs/apkit" target="_blank">https://github.com/fedi-libs/apkit</a>

---

**apkit** is a modern, fast, and powerful toolkit for building ActivityPub-based applications with Python, based on standard Python type hints.

The key features are:

* **FastAPI-based Server**: Build high-performance, production-ready ActivityPub servers with the power and simplicity of FastAPI.
* **Async Client**: Interact with other Fediverse servers using a modern `async` HTTP client.
* **Built-in Helpers**: Simplified setup for Webfinger, NodeInfo, HTTP Signatures, and other Fediverse protocols.
* **Extensible**: Designed to be flexible and easy to extend for your own custom ActivityPub logic.

## Requirements

* Python 3.12+
* [FastAPI](https://fastapi.tiangolo.com/) for the server part.
* [apmodel](https://github.com/fedi-libs/apmodel) for ActivityPub models.
* [apsig](https://github.com/fedi-libs/apsig) for HTTP Signatures.

## Installation

```bash
pip install apkit
```

To include the server components (based on FastAPI), install with the `server` extra:

```bash
pip install "apkit[server]"
```

## Example

Create a simple ActivityPub actor and serve it:

```python
from apkit.models import Person
from apkit.server import ActivityPubServer
from apkit.server.responses import ActivityResponse

app = ActivityPubServer()

HOST = "example.com"

actor = Person(
    id=f"https://{HOST}/actor",
    name="apkit Demo",
    preferredUsername="demo",
    inbox=f"https://{HOST}/inbox",
)

@app.get("/actor")
async def get_actor():
    return ActivityResponse(actor)

```

Run the server with `uvicorn`:

```bash
$ uvicorn main:app

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## License

This project is licensed under the terms of the MIT license.
