# Proposed Negotiated Match Configuration

Contract version: `0.1.0-proposed`
Status: **PROPOSED / UNFROZEN — CONFIG HASH DEFINED**

`config/game.json` is the neutral review fixture for the single authoritative shared
constitution. It contains all opponent-relevant terms, including response/watchdog
timeouts and Gatekeeper limits. Its source bytes must be identical between peers in
addition to producing the same canonical digest.

`config/rate_limits.json` is a local operational enforcement file beside private
TOML. This repository checks that its shared Gatekeeper mirror does not contradict
`game.json`, but its complete bytes and local extensions are not match terms.

## Participant agreement

Appendix B's `schema_version: "1.2"` example contains `agreed_between`, and the book
requires mutual per-match agreement and identical values. This candidate therefore
requires an explicit two-participant `agreed_between` value.

The representation is an ordered array of two unique, non-empty public `group_id`
values. The mutually agreed array order is byte-significant and preserved exactly;
implementations must not silently sort it. Exact character/length rules remain open.

## Match identity

`game_id`, `game_uid`, `links`, sub-game number, artifact filename, and the resulting
`config_sha256` belong to emitted artifact wrappers, not the source constitution.
Their common lifecycle is defined in `ARTIFACT_CONTRACT.md`.

## Configuration hash

Hash the complete parsed root object from `config/game.json`:

1. serialize object keys in lexicographic order;
2. use compact `,` and `:` separators with no insignificant whitespace;
3. preserve Unicode characters and encode the string as UTF-8;
4. compute SHA-256 and render 64 lowercase hexadecimal digits.

The artifact hash claim is external to the source object, so there is no self-hash
field to remove. `tests/fixtures/contracts/game-config-sha256.vector.json` records
the exact candidate vector.

## Agreement comparison

This package validates the proposed structure and Appendix F semantics, verifies the
operational rate-limit mirror, calculates/verifies the canonical config hash,
compares the exact source bytes, and compares offers semantically. Any participant,
negotiated value, timeout, Gatekeeper, hash, or source-byte mismatch must reject the
offer before play.
