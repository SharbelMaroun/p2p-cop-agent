# Proposed Negotiated Match Configuration

Contract version: `0.1.0-proposed`  
Status: **PROPOSED / UNFROZEN — P0 HASH BLOCKER**

`config/game.json` and `config/rate_limits.json` are a neutral review fixture for one
proposed match agreement. Their two-file split is a project proposal: Appendix B
names both paths but also embeds Gatekeeper values in its shared game example. The
lecturer must clarify whether the played agreement is one artifact or a split pair.

## Participant agreement

Appendix B's `schema_version: "1.2"` example contains `agreed_between`, and the book
requires mutual per-match agreement and identical values. This candidate therefore
requires an explicit two-participant `agreed_between` value.

The proposed representation is an ordered array of two unique, non-empty public
participant identifiers. Exact identifier format and deterministic ordering are not
established. The repository fixture uses neutral identities and does not restrict
valid opponents to this project's Cop and Thief.

## Match identity

Book table 20 establishes `config_<game_id>_g<NN>.json`; six sub-games are fixed.
The candidate therefore carries `game_id`, `sub_game_number`, and `config_name`, and
checks that the filename follows the book pattern at the application boundary.

`game_uid` is observed only in local generated artifacts and is not required here.
Which identity and link fields belong in the formal shared agreement still requires
lecturer clarification.

## Configuration hash blocker

Appendix F requires the agreement to be cryptographically locked, but the exact
`config_sha256` field, hash scope, self-hash exclusion, encoding, normalization,
number rendering, array ordering, whitespace, and final-newline rules are unresolved.

The candidate requires the `config_sha256` member but permits only `null` until those
rules are supplied. A non-null value must at least have a 64-lowercase-hex shape;
shape validation is not semantic hash verification. The active fixture remains
`null`, so it cannot authorize gameplay or contract freeze.

## Agreement comparison

Before canonicalization is defined, this package can:

1. validate the proposed structure and Appendix F fixed/minimum semantics;
2. compare two loaded configurations for semantic equality;
3. compare controlled contract files by exact bytes.

It cannot claim a cross-language canonical match hash. Any changed participant,
match identity, negotiated value, or Gatekeeper value must be rejected before play.
