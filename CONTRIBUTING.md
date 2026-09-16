# Contributing

Keep this a business-neutral template. Do not add live credentials, business data, automatic cron jobs, paid services or accounts. Preserve the exact runtime allowlist and user-data update tests.

1. Add a failing regression test before new executable behavior.
2. Keep runtime helpers standard-library-only and compatible with Python 3.10+.
3. Run the offline suite and validator with the development dependencies.
4. Run the actual Hermes installer/update harness in its disposable environment.
5. Update capability claims, CLI examples, linked skill table, limitations and test evidence.
6. Request independent security/logic review before commit or release.

Official platform documentation outranks folklore. Distinguish an implemented adapter from a procedural skill or user-connected tool. Never promise search rankings or AI citations. Do not expand publisher permissions without a new threat model and tests. Do not remove uncertain-write or single-attempt protections to make a demo pass.

Model-behavior and live-CMS tests require explicit separately approved fixtures/accounts. Offline tests do not prove either. See [testing](docs/testing.md).
