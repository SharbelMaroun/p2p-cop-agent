# Team Information

Team identity is verified team input, supplied directly by the team on 2026-07-28 and
recorded here on 2026-07-31 (`U-016`). Official addresses and repository roles are
directly confirmed.

| Field | Status | Value / evidence |
|---|---|---|
| Team/group name | CONFIRMED | `sharNamr` — verified team input, 2026-07-28 (`U-016`) |
| Group ID/number | CONFIRMED | `sharNamr` — the group identifier and the team code are deliberately the same string (`U-016`) |
| Member names/IDs | CONFIRMED | Amr safadi; Sharbel Maroun — verified team input, 2026-07-28 (`U-016`) |
| Eight-character team code | CONFIRMED | `sharNamr` — exactly eight characters, no spaces; satisfies Appendix E rule 45 (`U-016`) |
| Cop repository | CONFIRMED | <https://github.com/SharbelMaroun/p2p-cop-agent> |
| Thief repository | CONFIRMED | <https://github.com/SharbelMaroun/p2p-thief-agent> |
| General/repository-sharing address | CONFIRMED | `rmisegal@gmail.com` — lecturer answer `AF-020` |
| Automated-report address | CONFIRMED | `rmisegal+uoh26finalgame@gmail.com` — lecturer answer `AF-020` |
| Proposed contract | PROPOSED | `0.2.8-proposed`, UNFROZEN pending independent peer acceptance |

Do not infer identity fields from Git authors, examples, translations, or archived
configuration. The values above were supplied directly by the team; that direct input is
their authority.

## Notes on these values

- The group identifier and the Moodle team code are deliberately the same string,
  `sharNamr`. They serve different purposes and are not required to match: the group
  identifier is exchanged publicly, while the team code is a submission field.
- `sharNamr` is therefore the value that will appear in `agreed_between` in a real shared
  `config/game.json`. Both peers of this team use it, and it must be byte-identical on
  both sides of any match.
- Because the identifier is reused as the code, the Moodle submission code will be visible
  to any opponent and in emitted artifacts. It is a grouping key rather than a credential,
  so this is recorded as a consequence, not a defect.
- Member names are recorded exactly as supplied, including capitalization.

## Address provenance

Both addresses are cited to lecturer answer `AF-020`, **not** to the book. The book's
Appendix F table 20 prints `rimesegal@gmail.com` and `rimesegal+uoh26finalgame@gmail.com`
for these two fields, and prints the example repository as `github.com/rimesegal/…`. The
`rmisegal` spelling used here is the one confirmed by the lecturer and matches the real
upstream repository. Treat the book's table-20 spelling as a source typo; an incorrect
reporting address silently loses game points under Appendix E rule 32.

Do not place secrets, credentials, keys, tokens, private ports, or per-turn
commitment nonces here.
