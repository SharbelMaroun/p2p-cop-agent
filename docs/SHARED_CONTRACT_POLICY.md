# Shared Contract Policy

This Cop repository must remain independently runnable and must never import from, mount, or depend on the Thief repository.

`UNKNOWN`: whether generic stateless protocol/domain code may be duplicated independently in both repositories, and how parity must be demonstrated.

Prohibited design basis:

- shared live memory or mutable state;
- filesystem coupling between repositories;
- runtime imports from the companion repository;
- silently copied or assumed configuration;
- calling draft/example configuration “signed,” “agreed,” or “byte-identical.”

Before a shared contract is implemented, obtain the official schemas and rules, resolve the agreement/signature process, record every confirmed field in the ledger, and establish an explicit cross-repository parity process. Private Cop settings must remain local and must not reveal strategy or secrets.
