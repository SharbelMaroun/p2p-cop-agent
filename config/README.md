# Configuration Status

`game.json` and `rate_limits.json` are the active **proposed, unfrozen** shared M1 contract.
They contain only source-backed common values and are validated by the proposed schemas under
`docs/schemas/`. They are not signed game artifacts and are not frozen until the Thief repository
accepts identical bytes and both parity checks pass.

`game.toml.example` is the only Cop-private configuration example. It is deliberately empty
because the private field schema is not accepted yet. A real `config/game.toml` is ignored and
must never be shared, signed, or added to the parity manifest.

The shared config uses Appendix B profile 1.2. Supplied reporting-artifact examples use profile
1.1. Both shared files also carry the independent guidelines-required configuration revision
`version: "1.00"`. ADR-003 preserves these distinct version domains; the code does not translate
between profiles.

Files under `config/drafts/` remain quarantined historical drafts and are never loaded. Former
Thief-role drafts remain archived under `archive/pre-audit/opposite-role-config/thief/`.

See `docs/contracts/SHARED_RULES.md`, ADR-004, and `scripts/check_shared_contracts.py`.
