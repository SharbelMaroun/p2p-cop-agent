# PRD — Gatekeeper and Reporting

Status: required shape, Appendix F limits, destinations, filename patterns, and
JSON-attachment rule are confirmed. Runtime delivery is not implemented.

## Confirmed behavior

- All external API calls go through one Gatekeeper providing limiting, FIFO queueing,
  backpressure, retries, monitoring, and DOS protection.
- Gmail reporting uses least-privilege send authorization; credentials and tokens are
  secrets and stay out of Git.
- Each side separately sends the signed final JSON as an attachment at the end of a
  legal game. A free-text final-report body is rejected; conflicting/missing reports
  yield zero for both.
- Both attachments must be byte-identical to the mutually agreed aggregate result.
- Required report **content** includes four repository links, each game’s commit
  hash, and total token consumption. This does not prove the exact JSON key
  requiredness/type schema.
- Rate-limit minimums are 30 requests/minute, 2 concurrent requests, 5-second base
  retry, 3 retries, and queue depth at least 100.
- General/repository address: `rmisegal@gmail.com`; automated report address:
  `rmisegal+uoh26finalgame@gmail.com`.

Sources: book Ch. 9/Appendix A; Appendix E rules 28–35/49/53/54; Appendix F tables
19/20; `PS-008`.

## Schema and implementation boundary

The four observed schema-1.1 exemplar key sets and filename patterns are recorded in
[ARTIFACT_TEMPLATE_BASELINE.md](ARTIFACT_TEMPLATE_BASELINE.md). Formal
required/optional, exhaustive type/enum, conditional, and compatibility constraints
remain unresolved. ADR-003 isolates these fixtures from shared config schema 1.2;
ADR-010 owns Gmail delivery choices.

The behavior-free milestone may validate configuration and fixtures. It does not
implement a Gatekeeper or Gmail/reporting runtime.
