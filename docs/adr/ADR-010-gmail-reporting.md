# ADR-010 — Gmail Reporting

Status: **SOURCE-BOUND PLACEHOLDER — RUNTIME DEFERRED**

## Context

Automated reports go to `rmisegal+uoh26finalgame@gmail.com` as signed JSON
attachments. A free-text final-report body is rejected. Gmail authorization is
send-only/least-privilege, credentials are secret, and all external calls pass
through the Gatekeeper. `rmisegal@gmail.com` is the separate general/repository
address.

## Decision required

Select the provider-neutral client boundary, exact empty/body metadata behavior,
retry/idempotency interaction, and test/mocking approach without placing OAuth files
or credentials in the repository.

## Acceptance

- Fixture test proves correct destination, JSON attachment, and no free-text body.
- Gatekeeper and duplicate-send behavior are tested with mocks.
- Credentials/tokens are ignored and secret scanning passes.
- Artifact schema constraints assert only authoritative evidence.

No Gmail call or OAuth flow is implemented in M0–M1.
