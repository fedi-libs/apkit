# Agent Guidelines for apkit

This file provides guidelines for AI agents working on the apkit codebase.

## Project Overview

apkit is a modern, fast toolkit for building ActivityPub-based applications with Python. It uses FastAPI for the server, supports async HTTP clients, and handles ActivityPub models, HTTP signatures, and Fediverse protocols.

## Build, Test, and Lint Commands

### Package Manager
This project uses `uv` as the package manager.

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/apkit

# Run a single test
uv run pytest tests/path/to/test_file.py::test_function_name

# Run tests for a specific module
uv run pytest tests/client/
```

### Linting and Formatting
```bash
# Check all files with ruff
uv run ruff check .

# Check and auto-fix issues
uv run ruff check --fix .

# Format all files
uv run ruff format .

# Type checking with pyrefly
uv run pyrefly check .
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

## Code Style Guidelines

### Imports
1. **Standard library** imports first (e.g., `import json`, `from typing import ...`)
2. **Third-party** imports second (e.g., `import apmodel`, `from fastapi import ...`)
3. **Local/apkit** imports last (e.g., `from ..types import ActorKey`)
4. Use **absolute imports** for external dependencies, **relative imports** for internal modules
5. Sort imports with `collections.abc` before `typing`

Example:
```python
import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, Dict, List, Optional, TypeVar

import aiohttp
import httpx
from apmodel.types import ActivityPubModel

from ..types import ActorKey
from .models import Resource
```

### Formatting
- **Line length**: 88 characters (Black-compatible)
- **Indent**: 4 spaces
- **Quotes**: Double quotes for strings
- Follow **ruff** configuration in `pyproject.toml`

### Type Hints
- **Always use type hints** for function parameters and return types
- Use `from typing import ...` imports at the top
- Use `ParamSpec` and `TypeVar` for generic types
- For Python 3.10+, use `X | Y` syntax instead of `Optional` or `Union` where appropriate

Example:
```python
from typing import Optional, TypeVar

T = TypeVar("T")

def fetch(url: str, headers: Optional[dict] = None) -> dict | None:
    ...
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `ActivityPubClient`, `WebfingerResult`)
- **Functions/Methods**: `snake_case` (e.g., `fetch_actor`, `build_webfinger_url`)
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Private methods/vars**: Prefix with underscore (e.g., `__fetch_actor`, `_client`)
- **Type variables**: Single uppercase letter (e.g., `T`, `P`, `R`)

### Data Classes
- Use `@dataclass(frozen=True)` for immutable models
- Use regular `@dataclass` for mutable response wrappers
- Document classes and methods with docstrings

Example:
```python
@dataclass(frozen=True)
class Link:
    """Represents a link in a WebFinger response."""
    rel: str
    type: str | None
    href: str | None
```

### Error Handling
- Use **specific exceptions** (e.g., `ValueError`, `TypeError`)
- Raise with descriptive messages
- Use custom exceptions in `exceptions.py` for domain-specific errors
- Use `match` statements for pattern matching (Python 3.11+)

Example:
```python
match headers:
    case Mapping() as m:
        items = m.items()
    case None:
        items = []
    case _:
        raise TypeError(f"Unsupported header type: {type(headers)}")
```

### Testing
- Use **pytest** for testing
- Write **descriptive test names** (e.g., `test_build_webfinger_url`)
- Use pytest classes for grouping related tests (e.g., `class TestResource:`)
- Mock external dependencies when appropriate

### Project Structure
```
src/apkit/
├── __init__.py          # Package exports
├── _version.py          # Version info (auto-generated)
├── abc/                 # Abstract base classes
├── cache.py             # Caching utilities
├── client/              # HTTP client implementation
│   ├── __init__.py
│   ├── base/            # Base context managers
│   ├── client.py        # Main ActivityPubClient
│   ├── exceptions.py    # Client exceptions
│   ├── models.py        # Data models
│   └── types.py         # Type definitions
├── config.py            # Configuration
├── helper/              # Helper utilities
├── kv/                  # Key-value store implementations
├── models/              # ActivityPub model exports
├── nodeinfo/            # NodeInfo implementation
├── server/              # FastAPI server components
│   ├── app.py           # ActivityPubServer
│   ├── routes/          # Route handlers
│   ├── responses.py     # Response classes
│   └── types.py         # Server types
└── types.py             # Common types
```

## Important Notes

- Python **3.11+** is required
- **Type hints are mandatory** for all new code
- Follow the **KISS principle** - Keep It Simple, Stupid
- **Conventional Commits** for commit messages (e.g., `feat:`, `fix:`, `docs:`)
- The codebase is **not stable** - API changes may break backward compatibility

## Dependencies

Key external dependencies:
- `apmodel>=0.5.1` - ActivityPub models
- `apsig>=0.6.0` - HTTP signatures
- `fastapi>=0.116.1` - Web framework (optional, server extra)
- `aiohttp>=3.13.3` - Async HTTP client
- `httpx>=0.28.1` - Sync HTTP client

## Before Submitting

1. Run `uv run ruff check --fix .` to auto-fix linting issues
2. Run `uv run ruff format .` to format code
3. Run `uv run pyrefly check .` to verify type hints
4. Run `uv run pytest` to ensure all tests pass
5. Ensure imports are organized correctly
