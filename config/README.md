# Configuration Status

There is no active `game.json` in this directory. The stable
`shared_contract/` subtree contains schemas and examples only; each real match
supplies its shared game object by an explicit runtime path. That complete object is
hashed by `config_sha256`, while its exact source bytes have a separate hash.

`rate_limits.json` is an example local file-backed enforcement mirror beside private
TOML. Each run supplies the chosen mirror by an explicit path. Its Gatekeeper block
must exactly equal the authoritative shared match object; local extensions and exact
file bytes are not opponent match terms or parity-controlled.

Stable public semantics and Appendix F status/ownership are specified in
`../docs/PARAMETERS_BASELINE.md`. The per-match model is documented in
`../shared_contract/MATCH_CONFIGURATION.md`.

`game.toml.example` is Cop-private. A real `config/game.toml` is ignored and must
never be shared, signed, or added to the parity manifest. Ports, local opponent URL
storage, models, credentials, strategies, secrets, and per-turn commitment nonces
remain private. The public pre-play negotiation challenge is wire data, not private
configuration.

The match-object schema accepts only Appendix B profile 1.2. Local generated
artifacts use 1.1 and the simulator runtime uses 1.3; the code does not translate
among them.

Files under `drafts/` remain quarantined historical drafts and are never loaded.
Former opposite-role drafts remain archived under
`../archive/pre-audit/opposite-role-config/thief/`.

See `../shared_contract/SHARED_RULES.md`, `../docs/adr/ADR-003-schema-version-discrepancy.md`,
ADR-004/006, and the read-only `../shared_contract/verify.py`. Only the owner tool
`../scripts/generate_shared_manifest.py` regenerates the manifest.
