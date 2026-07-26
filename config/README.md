# Configuration Status

`game.json` and `rate_limits.json` are a neutral **proposed, unfrozen** negotiated
match fixture. The two-file split, field placement, root revision fields, JSON Schema
shape, and extension policy are project proposals. They are not signed game artifacts
and cannot authorize gameplay while `config_sha256` canonicalization is unresolved.

Stable public semantics and Appendix F status/ownership are specified separately in
`docs/contracts/LEAGUE_CONTRACT.md`. The per-match model is documented in
`docs/contracts/MATCH_CONFIGURATION.md`.

`game.toml.example` is Cop-private. A real `config/game.toml` is ignored and must
never be shared, signed, or added to the parity manifest. Ports, local opponent URL
storage, models, credentials, strategies, secrets, and nonces remain private.

The candidate accepts only Appendix B example profile 1.2. Local generated artifacts
use 1.1 and the simulator runtime uses 1.3; the code does not translate among them.

Files under `config/drafts/` remain quarantined historical drafts and are never loaded. Former
Thief-role drafts remain archived under `archive/pre-audit/opposite-role-config/thief/`.

See `docs/contracts/SHARED_RULES.md`, ADR-003/004/006, and
`scripts/check_shared_contracts.py`.
