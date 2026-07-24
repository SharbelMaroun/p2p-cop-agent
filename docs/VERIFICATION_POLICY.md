# Verification Policy

## Admission rule

A requirement becomes `CONFIRMED` only when its wording and scope can be checked directly in an authoritative source, with version plus an exact page, table, section, announcement, template path, or commit-pinned code location.

Numerical values require direct Appendix F evidence. Mandatory rules require direct Appendix E evidence. JSON fields and filenames require the official Moodle templates unless the book directly and unambiguously defines them. Professional packaging and README rules require the official Professional Software Submission Guidelines v3.0.

## Evidence records

Each record must state:

- status (`CONFIRMED`, `CONFLICT`, or `UNKNOWN`);
- authoritative source and version;
- exact location;
- applicable peer or shared concern;
- repository and test impact;
- conflicts or interpretation limits.

Secondary material may identify where to look, but cannot close an item. Examples and simulator defaults remain illustrative unless the official sources make them binding.

## Change gate

Before Phase 1:

1. obtain readable official sources and templates;
2. resolve ledger unknowns for the subsystem;
3. record conflicts without silently choosing a side;
4. agree any permitted shared contract independently in both repositories;
5. implement only the confirmed scope.

No active configuration loader or validator may be built against the current draft files.
