# About apkit

`apkit` is a powerful toolkit for Python, designed with the philosophy of making ActivityPub implementation easy, simple, and intuitive for anyone.

## The Journey to apkit

The developer's journey into the Fediverse began with an interest in Misskey, which led to an attempt to build a custom ActivityPub server named Graphene (Hol0). However, this initial project was unsuccessful due to a lack of deep knowledge, particularly around the complexities of request signing.

The direct impetus for `apkit` came from the development of a new ActivityPub server project, **Kagura**. Several challenges became clear during its creation:

1.  **Lack of Libraries**: At the time, there was a scarcity of practical Python libraries for ActivityPub, and many existing options were under restrictive licenses (like GPL/AGPL). 
2.  **Inspiration**: The developer was heavily inspired by the `Fedify` framework in the JavaScript ecosystem and wanted to create a similarly powerful and developer-friendly toolkit for Python.
3.  **Necessity**: The work on Kagura led to the creation of smaller, focused libraries out of necessity. First came `apsig` to handle HTTP Signatures, followed by `apmodel` to provide a practical parser for Activity Streams 2.0. `apkit` was then born to integrate these components into a single, comprehensive framework.

## Core Philosophy and Design

`apkit` is designed to be modular, allowing developers to use its components independently or as a complete toolkit. It abstracts away the complexities of the ActivityPub protocol, enabling developers to focus on the core features of their applications and helping to enrich the Fediverse.

## Comparison with Alternatives

When choosing a library for your ActivityPub project in Python, it's helpful to understand the landscape. Here’s how `apkit` compares to other notable libraries.

### apkit

*   **Pros**: `apkit` offers a balance of flexibility and convenience. While it includes a FastAPI-based server component (`apkit.server`) for rapid development, the core toolkit itself is framework-agnostic. It was developed with an async-first approach but maintains synchronous support. Its permissive MIT license makes it suitable for a wide range of projects.
*   **Cons**: As a relatively new library, `apkit` is still immature compared to more established alternatives. The integrated server component is also dependent on FastAPI, which might be a limitation if you are committed to a different web framework.

### pyfed

*   **URL**: [dev.funkwhale.audio/funkwhale/pyfed](https://dev.funkwhale.audio/funkwhale/pyfed)
*   **Pros**: Developed by the team behind Funkwhale, `pyfed` is an async-first, framework-agnostic library that aims to be a complete and robust ActivityPub implementation. It excels in security and type safety, featuring comprehensive security measures.
*   **Cons**: It is licensed under the AGPL, which can be a significant constraint for commercial or closed-source projects.

### bovine

*   **URL**: [bovine.readthedocs.io](https://bovine.readthedocs.io/en/latest/)
*   **Pros**: `bovine` is highly modular, functioning more like a set of building blocks than a monolithic library. Its design philosophy influenced `apkit`.
*   **Cons**: Its structure may feel closer to a server implementation than a general-purpose toolkit, which could be less intuitive for developers looking for a simple library to integrate into an existing application.

### Fedify

*   **URL**: [fedify.dev](https://fedify.dev)
*   `Fedify` is a major source of inspiration for `apkit`'s design and developer experience. However, it is a **TypeScript/JavaScript library** and cannot be used directly in Python projects.

### Direct Implementation (Without a Library)

You might also consider implementing the ActivityPub protocol directly without relying on a third-party library.

*   **Pros**: This approach gives you complete control over every aspect of the implementation and avoids adding external dependencies to your project. For very simple use cases, this might seem viable.
*   **Cons**: The complexity of the ActivityPub specification is significant. As illustrated by the history of `apkit`, even experienced developers can face major hurdles with core components like HTTP Signatures. Building everything from scratch requires a deep understanding of the protocol, a substantial investment of time and effort, and the ongoing burden of maintenance and security. You would be "reinventing the wheel," which libraries like `apkit` are designed to prevent. If you still choose this path, it is highly recommended to use a dedicated library for HTTP Signatures, such as `apsig`, to handle this critical and complex part.
