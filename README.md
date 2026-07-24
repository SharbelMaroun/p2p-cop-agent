# P2P Cop Agent

This repository is reserved for the **Cop peer** of the “Distributed Cops-and-Robbers over a Peer-to-Peer Network” final project.

> Companion Thief repository: <https://github.com/SharbelMaroun/p2p-thief-agent>

## Requirements status

Phase 0 is an evidence audit only. Gameplay, networking, cryptography, strategy, LLM, Gmail, GUI, replay, reporting, packaging, and tests have **not** been implemented.

Do not use the older PRDs, plans, TODO list, or configuration drafts as implementation specifications. They contain unverified examples and are classified in [the repository audit](docs/REPOSITORY_AUDIT.md).

- [Requirements ledger](docs/REQUIREMENTS_LEDGER.md)
- [Unknown requirements](docs/UNKNOWN_REQUIREMENTS.md)
- [Specification conflicts](docs/SPECIFICATION_CONFLICTS.md)
- [Verification policy](docs/VERIFICATION_POLICY.md)

The authoritative-source hierarchy and evidence availability are recorded in [SOURCE_OF_TRUTH.md](docs/SOURCE_OF_TRUTH.md) and [SOURCE_INVENTORY.md](docs/SOURCE_INVENTORY.md).

## Cop scope

Subject to verification of the official specification, Cop-side design work will cover pursuit strategy, the Cop’s belief about the Thief, Thief-scent observations, legal barrier placement and budget, the capture objective and proof, the Cop’s verbal truth/bluff policy, and Cop-local state and private settings.

This repository must not import from, mount, or depend on the Thief repository. Whether generic stateless protocol/domain code may be independently duplicated here remains `UNKNOWN`; shared live state is not an accepted design basis.

## Academic report

The required README report structure, section count, evidence, submission tag rules, and screenshots remain placeholders until the official project book and Professional Software Submission Guidelines are directly verified.

## Installation and usage

`UNKNOWN` — no package manifest, lockfile, dependencies, CLI, ports, or commands are approved yet.

## Configuration

The files under `config/` are unverified drafts inherited from the initial scaffold. Their filenames, schemas, versions, values, and split between shared/private settings are not approved. They are quarantined by policy and must not be loaded by future code until the official templates and Appendix evidence are obtained.

## License

The repository currently contains an MIT license. Whether that license is appropriate for all future original code and compatible with the lecturer material is still under review; lecturer material is not relicensed here.
