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
## [0.3.3](https://github.com/fedi-libs/apkit/compare/0.3.2...v0.3.3) (2025-10-21)


### Features

* add (empty) outbox ([3db651b](https://github.com/fedi-libs/apkit/commit/3db651b0e6a2096b3d5db42fe05ada26c122e035))
* add abstruct classes for create apkit integration to easy ([6157fde](https://github.com/fedi-libs/apkit/commit/6157fde83ad8f698d05ddc0c46e3b8bf8f21ebb8))
* add example to like an object ([993f088](https://github.com/fedi-libs/apkit/commit/993f088ea4d74c253f0fa6efef4b649e57a0d8cb))
* add synchronous ActivityPubClient ([43a894e](https://github.com/fedi-libs/apkit/commit/43a894e15c167877970617f05bc25dfa81d1b7cc))
* add synchronous support for apkit client ([45f08ec](https://github.com/fedi-libs/apkit/commit/45f08ec31a8288d17aef2184372019828998295b))
* **client:** Add _is_expected_content_type to check expected ([0ba0c61](https://github.com/fedi-libs/apkit/commit/0ba0c618800bd595ff5a18d779084058119733f8))
* **client:** add ActivityPubClient in __init__.py ([8d2a53c](https://github.com/fedi-libs/apkit/commit/8d2a53cbea4ac3487ac5049e6f18f7e263c76a96))
* **client:** add multiple signature support to async-based ([9017bc7](https://github.com/fedi-libs/apkit/commit/9017bc74f9c99b45fc3f96153f0db8fb0aee218c))
* **client:** add multiple signature support to async-based ActivityPubClient ([7949998](https://github.com/fedi-libs/apkit/commit/794999895378975867b28be56c39d583f76a4e17))
* **client:** add User-Agent when User-Agent is not set ([9fc6957](https://github.com/fedi-libs/apkit/commit/9fc6957b5a300e3ec94452b491e2c02dc7b26ec9))
* example how to follow another accout ([dd84bfc](https://github.com/fedi-libs/apkit/commit/dd84bfc74999238b36e96446927c388dad657c02))
* parse command line arguments ([8b223c8](https://github.com/fedi-libs/apkit/commit/8b223c89220b370406a2d585a4d9e8337c147b2c))
* **release:** release automation ([4d2a42c](https://github.com/fedi-libs/apkit/commit/4d2a42cd3143c32d6892e63d2f7b71de2f47d7ed))
* **release:** release automation ([4afbad4](https://github.com/fedi-libs/apkit/commit/4afbad4e0f160af99323dc784bcae28eef0974cd))
* **test:** add initial unittests ([7bb990b](https://github.com/fedi-libs/apkit/commit/7bb990b49ee53388c00fe7d10b6207bf7e6e3188))


### Bug Fixes

* **ci:** add missing file to stable ([690dfd4](https://github.com/fedi-libs/apkit/commit/690dfd4fc93c66892d9136a491e6207282d25bf3))
* **ci:** add missing files for stable ([9cea65c](https://github.com/fedi-libs/apkit/commit/9cea65c48e179275a788bd4b92a3d74fbcf0a3e4))
* **ci:** fix typo ([22c61df](https://github.com/fedi-libs/apkit/commit/22c61dfb42a4bfa03a13e8343f20c2cd99eb0493))
* **ci:** fix typo ([8a3739d](https://github.com/fedi-libs/apkit/commit/8a3739d739b8b8abcc62cb9c033f383977c27881))
* **client:** async def but synchronous ([d0cc9ae](https://github.com/fedi-libs/apkit/commit/d0cc9ae4b47603141bdf4a443eea96fa49f29f6d))
* **client:** fix typo ([41ec6ee](https://github.com/fedi-libs/apkit/commit/41ec6eef9e717e12960e3fb9f1148ea6fb55e1c7))
* **client:** Follow Location header in redirect loop ([b45675c](https://github.com/fedi-libs/apkit/commit/b45675ca139d563061afed5e4ceaad3e5370398f))
* **client:** Prevent decoding bytes body in __sign_request ([b77d528](https://github.com/fedi-libs/apkit/commit/b77d528c2c4f1a520022907a63cece3aaea0cb51))
* **client:** Prevent overriding of sign_with=[] by using None as default ([3e3bacc](https://github.com/fedi-libs/apkit/commit/3e3bacc5b60644557bb31ff3d5187035e9d2294d))
* **client:** remove async text from docstring ([1c7c47d](https://github.com/fedi-libs/apkit/commit/1c7c47d1e30215a1dce4b738bc49f883ade03a9a))
* **client:** typo ([c825fbf](https://github.com/fedi-libs/apkit/commit/c825fbfdcd4ba1a026aaeedf7edb33472fb50eb1))
* **client:** WebfingerResource.url is not required any values ([5abb9bd](https://github.com/fedi-libs/apkit/commit/5abb9bd44ad6b94eb511a48a080ddbbbc4b782fc))
* on_follow_activity sends correct accept response ([57d77fd](https://github.com/fedi-libs/apkit/commit/57d77fd459a3886d0a52dd1b6a249956c0e095bc))
* **server:** Error message clarified when no handler is registered ([e409ead](https://github.com/fedi-libs/apkit/commit/e409eadc688dc4cfaa0c14756e1605f8a05bac0e))
* typo in help text ([4f8f8a2](https://github.com/fedi-libs/apkit/commit/4f8f8a26fb4a2882d0f2646938b64d323af80731))

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
