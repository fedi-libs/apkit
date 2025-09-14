# Working with Models

The ActivityPub object models used by `apkit` are provided by the `apmodel` library. These are defined as standard Python `dataclasses`, not Pydantic models.

This allows you to benefit from type hinting, autocompletion, and static analysis while working with lightweight and easy-to-handle objects for your ActivityPub data.

```python
from apkit.models import Person

# Can be instantiated like a normal dataclass
new_person = Person(
    id="https://example.com/new_person",
    name="New Person"
)
```
