# Shared Contract Policy

The Cop repository remains independently installable and runnable. It never imports,
mounts, or reads the Thief repository at runtime.

Contract `0.2.6-proposed` is **UNFROZEN**. Cop-local manifest integrity establishes
only that Cop files match Cop's recorded hashes. Cross-repository parity additionally
requires Thief acceptance and optional read-only comparison reporting identical
controlled bytes and an identical separately computed manifest hash.

## Boundaries

- Played-game shared JSON is byte-identical and cryptographically locked.
- Role-private TOML, `.env`, secrets, ports, tokens, providers, tunnel credentials,
  per-turn commitment nonces, and local strategy never enter the parity bundle.
  The public negotiation challenge appears only in its live wire message, not in
  stable or private configuration.
- Local generated-artifact key sets may be preserved as non-authoritative observation
  fixtures while provenance and formal constraints remain explicitly unresolved.
- Book example `1.2`, local-artifact observation `1.1`, and simulator runtime `1.3`
  remain separate; no normalization or compatibility is inferred.
- Missing, unexpected, or changed controlled files fail local integrity; the manifest
  remains outside its own file list and its exact-byte SHA-256 is reported separately.

## Prohibited claims/designs

- shared live memory, database, mutable state, or runtime filesystem;
- imports from the companion repository;
- silent copying of draft/example/simulator material;
- calling a proposal “signed,” “agreed,” “frozen,” or “byte-identical” without the
  required evidence;
- presenting simulator MCP names, envelope fields, or commit serialization as
  book-mandated.

Generic duplicated runtime code remains a separate permission/design question. The
proposed docs/config/schema/fixture bundle does not authorize a shared live package.
