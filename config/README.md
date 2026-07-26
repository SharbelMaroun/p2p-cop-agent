# Configuration Status

`game.json` is the neutral **proposed, unfrozen** shared constitution. It contains
all opponent-relevant terms and is the complete object hashed by `config_sha256`.
The hash is written later into each per-sub-game agreed-config artifact; it is not a
self-member of this source file.

`rate_limits.json` is the file-backed enforcement mirror. Its Gatekeeper values must
match `game.json` exactly; it does not create a second negotiated match identity.

Stable public semantics and Appendix F status/ownership are specified separately in
`docs/contracts/LEAGUE_CONTRACT.md`. The per-match model is documented in
`docs/contracts/MATCH_CONFIGURATION.md`.

`game.toml.example` is Cop-private. A real `config/game.toml` is ignored and must
never be shared, signed, or added to the parity manifest. Ports, local opponent URL
storage, models, credentials, strategies, secrets, and nonces remain private.

The source constitution accepts only Appendix B profile 1.2. Local generated
artifacts use 1.1 and the simulator runtime uses 1.3; the code does not translate
among them.

Files under `config/drafts/` remain quarantined historical drafts and are never loaded. Former
Thief-role drafts remain archived under `archive/pre-audit/opposite-role-config/thief/`.

See `docs/contracts/SHARED_RULES.md`, ADR-003/004/006, and
`scripts/check_shared_contracts.py`.
