# Useful Links

This page contains a curated list of links to specifications, protocols, and other resources relevant to `apkit` and Fediverse development.

## Specifications and Protocols

These are the core standards that `apkit` helps you implement.

*   **[ActivityPub](https://www.w3.org/TR/activitypub/)**: The main W3C recommendation for a decentralized social networking protocol.
*   **[ActivityStreams 2.0](https://www.w3.org/TR/activitystreams-core/)**: The data format used by ActivityPub to represent activities and objects.
*   **[Webfinger](https://datatracker.ietf.org/doc/html/rfc7033)**: A protocol for discovering information about people or other entities on the internet, used in the Fediverse to find user accounts.
*   **[HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12)**: The mechanism used to secure messages between servers.
*   **[NodeInfo](https://nodeinfo.diaspora.software/)**: A protocol for exposing standardized metadata about a server.

## apkit-related Guides and Resources

This section includes links to the source code for `apkit` and its core dependencies, as well as articles and community resources.

### Project Repositories

*   **[apkit Source Code](https://github.com/fedi-libs/apkit)**: The main repository for the `apkit` toolkit.
*   **[apmodel Source Code](https://github.com/fedi-libs/apmodel)**: The library that provides the `dataclass`-based models for ActivityStreams 2.0 objects.
*   **[apsig Source Code](https://github.com/fedi-libs/apsig)**: The library used for handling HTTP Signatures.

### Community
!!! tip "Add your project!"
    Are you using `apkit` in your project? We'd love to feature it here! Please [open a pull request](https://github.com/fedi-libs/apkit/pulls) to add it to the list.

*   **[How to Build a Simple ActivityPub Reminder Bot in Python](https://hackers.pub/@cocoa/2025/how-to-build-a-simple-activitypub-reminder-bot-in-python) ([PythonとActivityPubでリマインダーBotを作ろう](https://zenn.dev/amasecocoa/articles/1449d43069d549#%E3%81%BE%E3%81%A8%E3%82%81))** by @AmaseCocoa

## Developer Resources

General resources that are useful when contributing to `apkit`.

*   **[Conventional Commits](https://www.conventionalcommits.org/)**: The specification for formatting commit messages, which is used in the `apkit` project.
