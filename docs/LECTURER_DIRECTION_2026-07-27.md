# Lecturer-Direction Transcription Supplied on 2026-07-27

## Evidence status

The project owner supplied a detailed transcription on 2026-07-27 and identified it
as the current instructions from Dr. Yoram Segal. This record preserves that
direction and separates it from claims independently verified in the local book,
the four supplied JSON files, and the pinned simulator.

The transcription is actionable project-owner direction. It is not an authenticated
Moodle export, signed lecturer message, or original template archive. Therefore it
does not, by itself, authenticate the provenance of the four local JSON files or
define omitted formal JSON-Schema rules.

## Independently corroborated direction

| Direction | Direct local corroboration |
|---|---|
| A counted series has six sub-games | Book Appendix F table 18 |
| Shared terms live in byte-identical `config/game.json`; peer-local values live in `config/game.toml` | Book Appendix B, printed pp. 110-116 |
| Shared JSON supports sorted-key canonical serialization and `config_sha256` | Book Appendix B, printed p. 111 |
| `agreed_between` is a two-ID JSON list | Book Appendix B example, printed p. 113; supplied agreed-config bytes |
| Four artifact filename families | Book table 20; all four supplied artifacts |
| All four supplied artifacts carry `game_id`, `game_uid`, and `links` | Direct key-set inspection |
| Declaration includes per-group hardware data; the log seals a step-0 `system_spec` record | Direct artifact inspection |
| Roles alternate: natural role on odd games, opposite role on even games | Pinned simulator README and `sdk/series.py`; lecturer-direction transcription supplies the higher-level requirement |
| Canonical config hashing uses sorted keys, compact `,`/`:` separators, UTF-8, and SHA-256 | Lecturer-direction transcription; pinned simulator `report/artifact_helpers.py` corroborates the algorithm |
| Each side independently sends the agreed result JSON attachment | Book Chapter 9, Appendix E rules 32-35 |
| Automated destination is `rmisegal+uoh26finalgame@gmail.com` | Book table 20 |
| Individual Moodle submission, immutable form layout, PDF export, and eight-character team code | Appendix E rules 43-45 |

The supplied agreed-config hash was independently reproduced. Its
`config_sha256` is the SHA-256 of compact sorted-key UTF-8 JSON for the simulator's
source shared terms with source profile `1.3`. The emitted artifact itself reports
profile `1.1`. This confirms that source-config and artifact schema versions are
separate domains; it does not establish compatibility between them.

## Project decisions authorized by the transcription

- Preserve the exact order of the two mutually agreed `group_id` values in
  `agreed_between`; do not silently sort or normalize them.
- Treat `config/game.json` as the single authoritative shared constitution.
- Compute `config_sha256` over the complete parsed shared-config object. The hash is
  stored in the per-sub-game config artifact, not inside the hashed source object,
  so there is no self-hash member to exclude.
- Serialize that object with lexicographically sorted keys, compact separators,
  unescaped Unicode encoded as UTF-8, no insignificant whitespace, and SHA-256.
- Use six sub-games and the odd-natural/even-opposite role schedule.
- Keep the baseline move decision in pure Python. LLM movement is disabled unless a
  future mutually agreed contract revision explicitly enables it.
- Treat the four artifact names as four families: one declaration, six config
  artifacts, six log artifacts, and one aggregate result for a six-game series.
- Require the final submitted tag literal `v1.0-submission`, subject to a last
  current-Moodle check immediately before release.

## Still unresolved

- Authentic official provenance and complete required/optional/type/conditional
  rules for the four supplied JSON files.
- A complete artifact compatibility policy beyond source config `1.2`, observed
  artifact `1.1`, and simulator runtime/source `1.3`.
- Exact allowed `game_id` characters and the UUID version/creation method.
- Whether `links.config` and `links.log` must contain a literal `<NN>` pattern or a
  resolved per-sub-game filename in every artifact family.
- Commit-reveal payload canonicalization, delimiter/domain binding, and nonce size;
  the config-hash decision does not resolve the move-commit protocol.
- Current Moodle announcements, deadline, exact PDF filename, and the original
  artifact-template handoff.
