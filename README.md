# P2P Cop Agent

This repository is assigned to the **Cop peer** of the “Distributed Cops-and-Robbers over a Peer-to-Peer Network” final project.

> Companion Thief repository: <https://github.com/SharbelMaroun/p2p-thief-agent>

## Requirements status

The repository is in the **verified-requirements phase**. Gameplay, FastMCP runtime code, strategy, cryptography, Gmail, GUI, replay, reporting, packaging, and tests have not been implemented.

- [Requirements ledger](docs/REQUIREMENTS_LEDGER.md)
- [Unknown requirements](docs/UNKNOWN_REQUIREMENTS.md)
- [Specification conflicts](docs/SPECIFICATION_CONFLICTS.md)
- [Verification policy](docs/VERIFICATION_POLICY.md)
- [Repository audit](docs/REPOSITORY_AUDIT.md)
- [Configuration status](config/README.md)

Legacy PRDs, plans, tasks, and configuration drafts contain unverified runtime details. Their quarantine notices remain controlling until the relevant requirements are confirmed.

## Confirmed structural requirements

The shared baseline is maintained in [SHARED_REQUIREMENT_BASELINE.md](docs/SHARED_REQUIREMENT_BASELINE.md).

- `SR-001`–`SR-003`: use separate Cop and Thief repositories, cross-link them, and make both accessible to the lecturer.
- `SR-004`: run the peers as separate processes and configuration environments without shared live mutable state or access to the opponent’s private truth.
- `SR-005`: each peer acts as both a FastMCP server and FastMCP client. Exact tool names remain `UNKNOWN`.
- `SR-006`: each repository contains at least a root README, configuration directory, PRD documents, PLAN, TODO, and code when implementation begins.
- `PS-001`: maintain the mandatory README, core planning documents, and dedicated mechanism PRDs.
- `PS-002`: use `uv`, with `pyproject.toml` as the dependency source of truth and a committed `uv.lock`; those files are intentionally not created in this remediation.
- `PS-003`–`PS-005`: keep code/tests within the confirmed line limit, use TDD with the confirmed coverage floor, and pass the official Ruff configuration.
- `PS-006`: keep configurable values out of code and secrets out of Git.
- `PS-007`–`PS-008`: preserve an SDK/service boundary and route external API calls through a centralized gatekeeper.
- `PS-009`: maintain the prompt-engineering log at [docs/PROMPT_LOG.md](docs/PROMPT_LOG.md).

## Cop scope

Candidate Cop concerns are pursuit, belief about the Thief, Thief-scent observation, legal barrier placement, capture, Cop-local strategy, and Cop-local verbal behavior.

Their exact mechanics, fields, values, proofs, and timing remain subject to direct Appendix E/F and official-template verification. This repository must not depend on the Thief repository filesystem or import its private runtime code.

## Installation and usage

Not published yet. Package metadata, dependencies, runtime entry points, and active configuration are intentionally absent during requirements verification.

## Configuration

There is no approved runtime configuration. Historical Cop drafts are quarantined under `config/drafts/cop/`; opposite-role drafts are preserved outside the active configuration tree under `archive/pre-audit/opposite-role-config/thief/`. See [config/README.md](config/README.md).

## License

The existing MIT license applies only to team-authored material where legally valid. Lecturer-provided documents and code are not automatically relicensed. The final licensing decision remains subject to review.
