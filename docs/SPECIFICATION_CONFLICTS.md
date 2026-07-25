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
| C-008 | CONFLICT | Appendix B shared config uses schema 1.2; official artifact examples use 1.1 | ADR-003 isolates shared game/rate 1.2 from reporting-artifact fixture 1.1; no silent normalization. |
| C-009 | CONFIRMED | Simulator subtractive scent versus book multiplicative scent | Book Ch. 4 controls; use `max(0,(1-ρ)τ+Δτ)`. ADR-005 records the decision. |
| C-010 | UNKNOWN | Whether simulator source may be copied into this public MIT repository | Educational-use EULA/provenance review or lecturer permission is required. ADR-008 defaults to no substantial copying. |

No unresolved row is closed by selecting a simulator/example default.
