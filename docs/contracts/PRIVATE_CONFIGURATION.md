# Private Peer Configuration Boundary

Status: **PROPOSED / LOCAL ONLY**

Each peer owns its local configuration independently. Appendix B establishes that
the agreed shared JSON overrides overlapping private TOML values; it does not permit
one peer to inspect the other's file or runtime filesystem.

Private-only concerns include:

- bind host and port;
- local storage of the opponent's public URL;
- tunnel provider and credentials;
- LLM/provider/model selection and API credentials;
- private strategy, heuristics, weights, and tuning;
- local paths, caches, telemetry destinations, and debugging switches;
- secrets, tokens, nonces, and signing material.

`config/game.toml.example` is Cop-local and is excluded from the parity manifest.
Real `config/game.toml` and `.env` files remain ignored. A public field later proven
mandatory by an authenticated course schema must be reviewed explicitly rather than
silently copied from private configuration.

`config/rate_limits.json` is a file-backed operational mirror, not a second source
of negotiated truth. Its Gatekeeper values must equal the authoritative signed
`config/game.json` section. Whether both repositories must retain the mirror with
identical bytes is still a parity-policy question, not permission for local values
to weaken the shared limits.
