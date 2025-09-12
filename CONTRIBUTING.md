
## How to Contribute

Thank you for your interest in contributing to `apkit`! To ensure a smooth collaboration, please read and follow these guidelines.

### Communication

We encourage all **Pull Requests** and **Issues** to be written in **English**. This helps more developers understand the context and participate in the discussion. If you're not a native English speaker, don't worry—just do your best! We appreciate any effort to make communication accessible to everyone.

---

### Code Standards

#### Type Hints
Please use **type hints** for all new code. This improves readability and allows for static analysis, which helps catch potential bugs early.

#### KISS Principle
We adhere to the **Keep It Simple, Stupid (KISS)** principle. Please write code that is as simple and straightforward as possible. Avoid overly complex logic or unnecessary code that could make future maintenance difficult for others.

---

### Commit Messages

All commit messages must follow the **Conventional Commits** specification. This makes our commit history clear and easy to read, and it helps with automated changelog generation.

**Examples of Conventional Commits:**

* `feat: add new feature`
* `fix: resolve a bug`
* `docs: update documentation`
* `refactor: refactor code without changing functionality`

---

### Pull Request Locations

To keep our projects organized, please submit your Pull Requests to the correct repository:

* **For signature verification/creation**, please submit your PR to the **`apsig`** repository.
* **For loading and outputting models** that include ActivityStreams, please submit your PR to the **`apmodel`** repository.
* Please submit Pull Requests for features that are not fundamental to apsig or apmodel, such as signature verification for requests sent to the inbox or double-knocking functionality for RFC9421-based signatures, to the apkit repository.