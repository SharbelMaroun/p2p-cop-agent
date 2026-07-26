# Lecturer Simulator Baseline

- Upstream: <https://github.com/rmisegal/Game-P2P-Cop-Chase>
- Required reference commit: `960499fd5e8777b4929625f5d8fdcf2ab4677b54`
- Role: learning and interoperability reference, **not** a submission skeleton

Any simulator observation used here must be tied to that exact commit, file/symbol,
command, and observed result. The Final Project Book, Appendix F, Appendix E,
authenticated official templates, current Moodle/lecturer clarification, and the
Software Submission Guidelines all outrank the simulator.

## Candidate observations, not book mandates

- `negotiate`, `receive_turn`, `submit_audit`, and `receive_control` are candidate
  tool names for ADR-001.
- The one-game demo/default does not replace the official six-sub-game series.
- The simulator’s subtractive scent decay must not replace the book’s multiplicative
  update; ADR-005 records that boundary.

## License and reuse

The upstream repository carries an educational-use EULA rather than this
repository’s MIT license. Reading, running, and inspecting its behavior/tests may
support coursework, but substantial copying, adaptation, redistribution, or
publication in this public repository requires the provenance/license decision in
ADR-008 and, where needed, lecturer permission. No simulator runtime source is an
implementation baseline.

No MCP name, message field, schema rule, provider, port, or default becomes mandatory
merely because the simulator uses it.
