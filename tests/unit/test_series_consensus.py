"""C-040: the post-series `series_consensus` envelope is acknowledged, never scored.

After game 6 of the 2026-08-12 series, `uoh-ay26` sent one extra `submit_audit` with
`result_claim: "series_consensus"`, empty records, and a `consensus_sha` over the six
agreed result rows. Our enum refused it. Harmless that night -- every log was already
written -- but a peer whose protocol ends with an acknowledged SHA exchange deserves
the acknowledgement, and silently refusing the finale is exactly the class of
over-strictness that C-033/C-037/C-038 catalogue.
"""

import pytest

from p2p_cop_agent.protocol.audit import AuditVerdict, audit_reveal
from p2p_cop_agent.protocol.messages import ProtocolError, validate_message


def consensus(**extra: object) -> dict:
    return {"sender": "thief", "records": [], "result_claim": "series_consensus",
            "consensus_sha": "ab" * 32, **extra}


def test_a_valid_consensus_envelope_passes_the_schema() -> None:
    validate_message("audit", consensus())


def test_a_consensus_with_records_is_malformed() -> None:
    """A consensus that smuggles records is not a consensus."""
    record = {"payload": {"step": 1}, "nonce": "ab" * 16, "commit": "c" * 64}
    with pytest.raises(ProtocolError):
        validate_message("audit", consensus(records=[record]))


def test_a_consensus_without_its_sha_is_malformed() -> None:
    body = consensus()
    del body["consensus_sha"]
    with pytest.raises(ProtocolError):
        validate_message("audit", body)


def test_a_malformed_sha_is_refused() -> None:
    with pytest.raises(ProtocolError):
        validate_message("audit", consensus(consensus_sha="not-hex"))


def test_audit_reveal_acknowledges_a_consensus_as_verified() -> None:
    report = audit_reveal(consensus())
    assert report.verdict is AuditVerdict.VERIFIED


def test_a_consensus_skips_the_live_commit_match() -> None:
    """No records means nothing to reproduce: the live-commit check must not fire.

    Passing `received_commits` from a real game would otherwise compare 15 live
    commits against zero revealed ones and cry tamper at the series' final message.
    """
    report = audit_reveal(consensus(), received_commits=("a" * 64, "b" * 64))
    assert report.verdict is AuditVerdict.VERIFIED


def test_game_result_claims_do_not_require_a_consensus_sha() -> None:
    """The extension must not leak requirements into ordinary audits."""
    record = {"payload": {"step": 1}, "nonce": "ab" * 16, "commit": "c" * 64}
    validate_message("audit", {"sender": "thief", "records": [record],
                               "result_claim": "survival"})
