# Specification Conflicts and Resolutions

This register is not byte-identical with the Thief repository at the compared
baseline; see [PARITY_REPORT.md](PARITY_REPORT.md).

| ID | Status | Conflict | Resolution / required action |
|---|---|---|---|
| C-001 | CONFIRMED | Example `num_games: 1` versus six sub-games | One is an example sub-game/default; Appendix F table 18 fixes a played series at six. Do not promote the demo default. |
| C-002 | CONFIRMED | “Five components plus link” versus “six README sections” | They are the same mapping: five content sections plus section 6 companion link (book PDF p. 97; rule 42). |
| C-003 | UNKNOWN | Exact MCP tool names | Simulator candidates are `negotiate`, `receive_turn`, `submit_audit`, `receive_control`; none is book-mandated. ADR-001 and Thief acceptance decide. |
| C-004 | CONFIRMED | Lecturer/report address spellings differed | Canonical values are `rmisegal@gmail.com` and `rmisegal+uoh26finalgame@gmail.com` (book PDF p. 157). |
| C-005 | CONFIRMED | Earlier text cited Appendix G for GitHub submission | Book v3.0.0 uses Appendix C. |
| C-006 | CONFIRMED | Existing docs claimed cross-repository byte parity | Baseline hashes differ and two claimed files are absent on Thief main. New contract remains unfrozen pending evidence. |
| C-007 | UNKNOWN | Duplicated stateless shared runtime package versus separate peers | A parity-controlled docs/config/fixture bundle is proposed; generic duplicated runtime code is not authorized by that proposal. |
| C-008 | CONFLICT | Appendix B shared config uses schema 1.2; local generated artifacts use 1.1; simulator runtime uses 1.3 | Record all three observations; do not normalize or claim compatibility without authoritative evidence. |
| C-009 | CONFIRMED | Simulator subtractive scent versus book multiplicative scent | Book Ch. 4 controls; use `max(0,(1-ρ)τ+Δτ)`. ADR-005 records the decision. |
| C-010 | UNKNOWN | Whether simulator source may be copied into this public MIT repository | Educational-use EULA/provenance review or lecturer permission is required. ADR-008 defaults to no substantial copying. |
| C-011 | UNKNOWN | Four local JSON files were called official templates but are byte-identical to generated simulator logs | Keep them as `NEEDS_MANUAL_REVIEW` observations until the original authenticated course handoff is supplied. |
| C-012 | RESOLVED | Appendix B names `game.json` and `rate_limits.json` but embeds Gatekeeper values in the signed game file | `game.json` is the authoritative byte-identical shared constitution and contains timeouts/Gatekeeper terms. `rate_limits.json` is local enforcement whose shared values may not weaken or contradict `game.json`; its bytes are not cross-repository match terms. |
| C-013 | RESOLVED | Supplied agreed-config artifact reports schema `1.1`, while its recorded hash was produced from source shared terms with schema `1.3` | Source-config and emitted-artifact schema domains are distinct. This repository accepts source config `1.2`; it does not translate artifact 1.1 or simulator 1.3. |
| C-014 | RESOLVED | “Four JSON files” can be read as four physical files despite per-sub-game config/log names | It means four artifact families. A six-game series emits one declaration, six configs, six logs, and one aggregate result per reporting peer. |
| C-015 | CONFLICT / M7 | Upgrade plan says UUIDv4, current simulator derives a SHA-256-based UUID, and the supplied UUID has no RFC version | Do not freeze UUID derivation in M1. Select and test one accepted M7 protocol. |
| C-016 | CONFIRMED DISTINCTION | Eight-character Moodle team code was treated as runtime `group_id` syntax | Keep the administrative team code separate; runtime IDs remain non-empty text pending an artifact schema. |
| C-017 | CONFIRMED DISTINCTION | Book table 20 was described as twenty controlled repository paths | Table 20 lists artifact variables, repository, and addresses. The parity manifest is an internal Cop-authored coordination tool. |
| C-018 | CONFIRMED DISTINCTION | Simulator `validate_agreement`/stub success was treated as M1 contract acceptance | It checks nine required normalized terms. M1 review/parity and future runtime Step-0 are separate gates. |

No unresolved row is closed by selecting a simulator/example default.
