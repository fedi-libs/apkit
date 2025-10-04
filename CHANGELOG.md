## [unreleased]

### 🚀 Features

- Add community resource "PythonとActivityPubでリマインダーBotを作ろう"
- 3.11 support
- New logo

### 🐛 Bug Fixes

- OutboxのメソッドがPOSTになっている
- Apkit can't avaliable without extra dependency of [server]

### 🚜 Refactor

- Remove Author's Resource
## [0.3.1](https://github.com/fedi-libs/apkit/releases/tag/0.3.1) - 2025-09-14

### 🚀 Features

- Docs

### 🐛 Bug Fixes

- Urlを渡された場合に処理できない問題
## [0.3.0](https://github.com/fedi-libs/apkit/releases/tag/0.3.0) - 2025-09-12

### 🚀 Features

- Allow ActivityStreams in apmodel format to be directly specified as data as an argument
- Rewrite
- Redis support

### 🐛 Bug Fixes

- Allow resource to parse even if resource is url (limited support)
- Remove verifier from outbox
- Remove debugging code
- *(server)* Remove debugging codes
- Update lockfile

### ⚙️ Miscellaneous Tasks

- Update changelog [skip ci]
- Changelog [skip ci]
- Bump package version
## [0.2.0](https://github.com/fedi-libs/apkit/releases/tag/0.2.0) - 2025-05-02

### 🚀 Features

- Demo
- Generic inbox function
- Webfinger support
- Request utility (based aiohttp)
- Add configuration item
- Exceptions
- Add webfinger types
- User-agent
- Inmemory/redis
- Signature
- Convert to resource string
- Rewritte
- Auto publish

### ⚙️ Miscellaneous Tasks

- Init
- Add gitignore
- Add initial code
- Test server
- Remove unused dependencies
- Update dependencies
- Remove notturno integration
- Tweak
- Add RedirectLimitError
- Some changes
