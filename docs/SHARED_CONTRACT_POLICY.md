# Shared Contract Policy

The Cop repository remains independently installable and runnable. It never imports,
mounts, or reads the Thief repository at runtime.

Contract `0.1.0-proposed` is **UNFROZEN**. Repository parity is established only by
an explicit controlled-file manifest, SHA-256 verification, Thief acceptance, and
matching checks in both repositories. A statement in prose is not parity evidence.

## Boundaries

- Played-game shared JSON is byte-identical and cryptographically locked.
- Role-private TOML, `.env`, secrets, ports, tokens, providers, tunnel credentials,
  nonces, and local strategy never enter the parity bundle.
- Known official template key sets may be preserved as fixtures while unknown formal
  constraints remain explicitly unclaimed.
- Shared config schema `1.2` and artifact key-set fixture schema `1.1` remain separate
  under ADR-003.
- Missing, unexpected, or changed controlled files fail the checker; the manifest
  does not hash itself.

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
