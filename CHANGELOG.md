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

## [0.3.7](https://github.com/fedi-libs/apkit/compare/v0.3.6...v0.3.7) (2025-12-31)


### Features

* add apsig's rfc9421 support ([1445a49](https://github.com/fedi-libs/apkit/commit/1445a49366be9146c602cf502ac51ddf315fbf1b))
* add apsig's rfc9421 support ([38ea682](https://github.com/fedi-libs/apkit/commit/38ea6823d59d937e99cb33f2eca9f10409b98e62))


### Bug Fixes

* fix imports ([39d8415](https://github.com/fedi-libs/apkit/commit/39d841537d1e3a42a225269515cbe4a109e91bf9))
* remove copied code from apsig ([782a01a](https://github.com/fedi-libs/apkit/commit/782a01a929fbcd18baa31f2c4241c19a6fd1dd51))
* remove tool.uv.sources ([c65fc94](https://github.com/fedi-libs/apkit/commit/c65fc9498a24e26eb8d445f2e585566213d59a38))
* remove warning ([c5131b5](https://github.com/fedi-libs/apkit/commit/c5131b5a1637097f53b15e189ce424ad311f3a58))
* update deps ([0fb21a6](https://github.com/fedi-libs/apkit/commit/0fb21a6177f426dd6fea068736c59dfab86cb580))

## [0.3.6](https://github.com/fedi-libs/apkit/compare/v0.3.5...v0.3.6) (2025-12-23)


### Bug Fixes

* **docs:** fix examples ([cfeb59a](https://github.com/fedi-libs/apkit/commit/cfeb59a0abcf5c7929c647631def62271c3bc570))
* **docs:** nodeinfo and examples ([e47c822](https://github.com/fedi-libs/apkit/commit/e47c822fb2ed3ea0c70cf38842f29806e88177e2))
* **server:** Nodeinfo support in ActivityResponse ([8426a95](https://github.com/fedi-libs/apkit/commit/8426a956c7cf664a7a25ce12251fe6a5b4c94418))

## [0.3.5](https://github.com/fedi-libs/apkit/compare/v0.3.4...v0.3.5) (2025-12-23)


### Features

* 3.11 support ([30ca51b](https://github.com/fedi-libs/apkit/commit/30ca51b08f465f95b947244ddd44b9b7382fcac7))
* add (empty) outbox ([3db651b](https://github.com/fedi-libs/apkit/commit/3db651b0e6a2096b3d5db42fe05ada26c122e035))
* add abstruct classes for create apkit integration to easy ([6157fde](https://github.com/fedi-libs/apkit/commit/6157fde83ad8f698d05ddc0c46e3b8bf8f21ebb8))
* add community resource "PythonとActivityPubでリマインダーBotを作ろう" ([e6ad120](https://github.com/fedi-libs/apkit/commit/e6ad1208f71cdf97fe30ae0d7bb5fe12b7c76da1))
* add configuration item ([27347b2](https://github.com/fedi-libs/apkit/commit/27347b2274137350e7c180219d3c921190c34d05))
* add example to like an object ([993f088](https://github.com/fedi-libs/apkit/commit/993f088ea4d74c253f0fa6efef4b649e57a0d8cb))
* add synchronous ActivityPubClient ([43a894e](https://github.com/fedi-libs/apkit/commit/43a894e15c167877970617f05bc25dfa81d1b7cc))
* add synchronous support for apkit client ([45f08ec](https://github.com/fedi-libs/apkit/commit/45f08ec31a8288d17aef2184372019828998295b))
* add test ci ([b584b8c](https://github.com/fedi-libs/apkit/commit/b584b8cf1506f2bbce461dd7f682fabd1aace3c4))
* add webfinger types ([e74abb6](https://github.com/fedi-libs/apkit/commit/e74abb67235ccbc5ea888c7c9b064afa3d461d4a))
* Allow ActivityStreams in apmodel format to be directly specified as data as an argument ([f17c7e7](https://github.com/fedi-libs/apkit/commit/f17c7e7850e8d7b49ef1c1b7a90b441d84173c00))
* auto publish ([9eaea0e](https://github.com/fedi-libs/apkit/commit/9eaea0e9361db5ebbf36851e9f1c40e3b86f1968))
* **client:** Add _is_expected_content_type to check expected ([0ba0c61](https://github.com/fedi-libs/apkit/commit/0ba0c618800bd595ff5a18d779084058119733f8))
* **client:** add ActivityPubClient in __init__.py ([8d2a53c](https://github.com/fedi-libs/apkit/commit/8d2a53cbea4ac3487ac5049e6f18f7e263c76a96))
* **client:** add multiple signature support to async-based ([9017bc7](https://github.com/fedi-libs/apkit/commit/9017bc74f9c99b45fc3f96153f0db8fb0aee218c))
* **client:** add multiple signature support to async-based ActivityPubClient ([7949998](https://github.com/fedi-libs/apkit/commit/794999895378975867b28be56c39d583f76a4e17))
* **client:** add User-Agent when User-Agent is not set ([9fc6957](https://github.com/fedi-libs/apkit/commit/9fc6957b5a300e3ec94452b491e2c02dc7b26ec9))
* convert to resource string ([e58cbd1](https://github.com/fedi-libs/apkit/commit/e58cbd1b5c9cbbbfb0e420f89d2f97c0cbdf9bd7))
* demo ([955664d](https://github.com/fedi-libs/apkit/commit/955664d027eba0a1e26bd6f04b18c7aa4d512f74))
* docs ([9304608](https://github.com/fedi-libs/apkit/commit/930460861c895325f98c9931b5f54cffbe83472f))
* example how to follow another accout ([dd84bfc](https://github.com/fedi-libs/apkit/commit/dd84bfc74999238b36e96446927c388dad657c02))
* exceptions ([920e00f](https://github.com/fedi-libs/apkit/commit/920e00ffcac469ac508f70c9ac24a4da161ba1b9))
* Generic inbox function ([3f8578e](https://github.com/fedi-libs/apkit/commit/3f8578e37dad02576c711ef6e432de4053d7c89c))
* inmemory/redis ([dec3513](https://github.com/fedi-libs/apkit/commit/dec35130a28031ee802c15806c37990485850dbe))
* new logo ([de77670](https://github.com/fedi-libs/apkit/commit/de77670efa9992d029076900b2d128c2b60ef240))
* **nodeinfo:** Add NodeinfoBuilder ([99f89e3](https://github.com/fedi-libs/apkit/commit/99f89e3e7102b1b838c8973c24027f1ee42946ff))
* **nodeinfo:** Add NodeinfoBuilder ([f6c6f26](https://github.com/fedi-libs/apkit/commit/f6c6f26e4ac0a434d9de257f22f2ff2cfee8e040))
* parse command line arguments ([8b223c8](https://github.com/fedi-libs/apkit/commit/8b223c89220b370406a2d585a4d9e8337c147b2c))
* redis support ([ef1ec39](https://github.com/fedi-libs/apkit/commit/ef1ec39296ae5df02cf1f7f0532dd5848ef79df5))
* **release:** release automation ([4d2a42c](https://github.com/fedi-libs/apkit/commit/4d2a42cd3143c32d6892e63d2f7b71de2f47d7ed))
* **release:** release automation ([4afbad4](https://github.com/fedi-libs/apkit/commit/4afbad4e0f160af99323dc784bcae28eef0974cd))
* request utility (based aiohttp) ([8f0b59e](https://github.com/fedi-libs/apkit/commit/8f0b59ee3c12f2bbeaf105e41ad67beaaeae1f21))
* rewrite ([d2c45fd](https://github.com/fedi-libs/apkit/commit/d2c45fd44b448e4e2fcce452e9e7afece36d6075))
* rewrite ([8eb27b4](https://github.com/fedi-libs/apkit/commit/8eb27b43d501011e7980bdfc8f84eea7dc49b6d7))
* rewritte ([9d7573c](https://github.com/fedi-libs/apkit/commit/9d7573c225ccb122d4e1d7922b9e8756a3f5f922))
* signature ([35d3e6c](https://github.com/fedi-libs/apkit/commit/35d3e6c86dfe4cbbadbfe3dfc0dc3cfa470ed7b6))
* **test:** add initial unittests ([7bb990b](https://github.com/fedi-libs/apkit/commit/7bb990b49ee53388c00fe7d10b6207bf7e6e3188))
* user-agent ([2c6142e](https://github.com/fedi-libs/apkit/commit/2c6142e693f6ecd78bacfcaf13059a511733b959))
* webfinger support ([052cbf6](https://github.com/fedi-libs/apkit/commit/052cbf67ae117529dd53875e7d41785af15b94da))


### Bug Fixes

* add pytest-cov ([037c97a](https://github.com/fedi-libs/apkit/commit/037c97a6fa6efc3e0b9e9885cdac020186260880))
* Allow resource to parse even if resource is url (limited support) ([abbefad](https://github.com/fedi-libs/apkit/commit/abbefad05db5b088ab6de06629aabc26da594cdf))
* apkit can't avaliable without extra dependency of [server] ([c19fb93](https://github.com/fedi-libs/apkit/commit/c19fb93ca8cc6ac5a2d279094b94bd3c710a3e2c))
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
* **client:** use correct user-agent in actor fetches ([5602dd9](https://github.com/fedi-libs/apkit/commit/5602dd980ad5519afa51a11ab9c1232ff73860a4))
* **client:** use correct user-agent in actor fetches ([a00c4f2](https://github.com/fedi-libs/apkit/commit/a00c4f236afa15c16b29486f95566f5869fb5b41))
* **client:** WebfingerResource.url is not required any values ([5abb9bd](https://github.com/fedi-libs/apkit/commit/5abb9bd44ad6b94eb511a48a080ddbbbc4b782fc))
* **docs:** improve to readability document ([605f385](https://github.com/fedi-libs/apkit/commit/605f385a43ae6a69f31e619cfc07a5d9987721f3))
* on_follow_activity sends correct accept response ([57d77fd](https://github.com/fedi-libs/apkit/commit/57d77fd459a3886d0a52dd1b6a249956c0e095bc))
* outboxのメソッドがPOSTになっている ([6d38946](https://github.com/fedi-libs/apkit/commit/6d389463a82ef7ab263c23f526f67fea9b9d817c))
* remove debugging code ([3d4c056](https://github.com/fedi-libs/apkit/commit/3d4c056a0718ac268fea4707e656ac7466b9a937))
* remove verifier from outbox ([bb39650](https://github.com/fedi-libs/apkit/commit/bb396503b5a6bd4de23cde9845404a10418e7d94))
* **server:** Error message clarified when no handler is registered ([e409ead](https://github.com/fedi-libs/apkit/commit/e409eadc688dc4cfaa0c14756e1605f8a05bac0e))
* **server:** remove debugging codes ([32c1945](https://github.com/fedi-libs/apkit/commit/32c19451e3559ba4e869a41f86ca5faa3bd51c32))
* support apmodel 0.5.1 ([4e26c19](https://github.com/fedi-libs/apkit/commit/4e26c19fed8ec175019a09a34bbb70851d4bc264))
* support apmodel 0.5.1 ([d570b34](https://github.com/fedi-libs/apkit/commit/d570b3408cc23cecdb3cc6c3caea38a1d6e72847))
* typo in help text ([4f8f8a2](https://github.com/fedi-libs/apkit/commit/4f8f8a26fb4a2882d0f2646938b64d323af80731))
* update lockfile ([a5f8279](https://github.com/fedi-libs/apkit/commit/a5f827980cbc325fc2d0ee1b994c43b8bc24e879))
* urlを渡された場合に処理できない問題 ([d39572b](https://github.com/fedi-libs/apkit/commit/d39572b45ae918628e10af866409a68d341d2fea))

## [0.3.4](https://github.com/fedi-libs/apkit/compare/v0.3.3...v0.3.4) (2025-12-23)


### Features

* add test ci ([b584b8c](https://github.com/fedi-libs/apkit/commit/b584b8cf1506f2bbce461dd7f682fabd1aace3c4))
* **nodeinfo:** Add NodeinfoBuilder ([99f89e3](https://github.com/fedi-libs/apkit/commit/99f89e3e7102b1b838c8973c24027f1ee42946ff))
* **nodeinfo:** Add NodeinfoBuilder ([f6c6f26](https://github.com/fedi-libs/apkit/commit/f6c6f26e4ac0a434d9de257f22f2ff2cfee8e040))


### Bug Fixes

* add pytest-cov ([037c97a](https://github.com/fedi-libs/apkit/commit/037c97a6fa6efc3e0b9e9885cdac020186260880))
* **client:** use correct user-agent in actor fetches ([5602dd9](https://github.com/fedi-libs/apkit/commit/5602dd980ad5519afa51a11ab9c1232ff73860a4))
* **client:** use correct user-agent in actor fetches ([a00c4f2](https://github.com/fedi-libs/apkit/commit/a00c4f236afa15c16b29486f95566f5869fb5b41))
* **docs:** improve to readability document ([605f385](https://github.com/fedi-libs/apkit/commit/605f385a43ae6a69f31e619cfc07a5d9987721f3))
* support apmodel 0.5.1 ([4e26c19](https://github.com/fedi-libs/apkit/commit/4e26c19fed8ec175019a09a34bbb70851d4bc264))
* support apmodel 0.5.1 ([d570b34](https://github.com/fedi-libs/apkit/commit/d570b3408cc23cecdb3cc6c3caea38a1d6e72847))

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
- _(server)_ Remove debugging codes
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
