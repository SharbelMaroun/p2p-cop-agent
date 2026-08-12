"""M5-10e: the audit is what makes a claimed outcome checkable.

Split from `test_sub_game.py` under `G-04`, at the seam that file already marked. The
two halves ask different questions: that module asks *what ends a sub-game*, this one
asks *what the peer is handed afterwards so the ending can be disproved*. Rule 19 makes
any mismatch a technical forfeit with no appeal, so the reveal must go out even when the
reveal is what loses us the game.

Helpers are shared rather than duplicated, following the existing convention in this
suite of importing them across test modules.
"""

import pytest

from p2p_cop_agent.domain.scoring import Outcome
from p2p_cop_agent.orchestration.sub_game import RESULT_CLAIMS
from p2p_cop_agent.orchestration.turn_loop import TurnLoopError
from p2p_cop_agent.protocol.commit_reveal import verify_audit
from tests.unit.test_sub_game import Opponent, play, turn
from tests.unit.test_turn_loop import Sink


def test_the_audit_reveals_every_sealed_turn_and_recomputes() -> None:
    """`[AE-19]`: what we send must reproduce, or we score zero for both sides."""
    result = play(Opponent(*(turn(s) for s in range(1, 4))), threshold=3)

    assert result.audit is not None
    assert len(result.audit["records"]) == 3
    assert verify_audit(result.audit) is True


def test_the_step_zero_attestation_opens_the_audit() -> None:
    """`AE-024`, agreed with uoh-ay26 2026-08-12: peers reject an audit whose records do not
    open with a step-0 `system_spec` attestation. It rides the audit only, once, first.

    **Built with the real production builder, not a hand-made fixture (`C-041`).** The
    first version of this test hand-wrote a correct-shaped payload, so it passed while
    `build_step_zero` itself emitted no `step`/`type` members -- and the opponent's
    parser rejected every live Police audit as `[-1, 0]` while this test stayed green.
    A pin that does not exercise the producer pins nothing.
    """
    from p2p_cop_agent.protocol import HostSpec
    from p2p_cop_agent.protocol.attestation import build_step_zero, seal_step_zero

    payload = build_step_zero(
        host=HostSpec(os="test-os", cpu_type="x86_64", cpu_freq_mhz=3600, cpu_cores=1,
                      ram_gb=16, gpu_model="none", vram_gb=0),
        model="template", group_id="sharnamr", game_id="game-test",
        git_commit="a" * 40, config_sha256="b" * 64,
    )
    sealed = seal_step_zero(payload)
    step_zero = {"payload": sealed.payload, "nonce": sealed.nonce, "commit": sealed.commit}

    result = play(Opponent(*(turn(s) for s in range(1, 4))), threshold=3, step_zero=step_zero)

    records = result.audit["records"]
    assert records[0]["payload"]["step"] == 0
    assert records[0]["payload"]["type"] == "system_spec"
    assert len(records) == 4                      # step 0 + three moves, no duplicate
    assert verify_audit(result.audit) is True     # every record, step 0 included


def test_the_audit_claim_matches_the_outcome() -> None:
    captured = play(Opponent(turn(1, claim_response={"claim": [3, 3], "caught": True})))
    assert captured.audit["result_claim"] == RESULT_CLAIMS[Outcome.CAPTURE] == "capture"

    survived = play(Opponent(*(turn(s) for s in range(1, 4))), threshold=3)
    assert survived.audit["result_claim"] == "survival"


def test_the_audit_is_delivered_to_the_opponent() -> None:
    class Recorder(Sink):
        def __init__(self) -> None:
            super().__init__()
            self.audits: list[dict] = []

        def submit_audit(self, payload: dict) -> dict:
            self.audits.append(payload)
            return {"ok": True}

    peer = Recorder()
    play(Opponent(turn(1), turn(2)), threshold=2, transport=peer)
    assert len(peer.audits) == 1
    assert verify_audit(peer.audits[0]) is True


def test_a_technical_loss_still_sends_its_audit() -> None:
    """Withholding the reveal would make the loss uncheckable, which helps nobody."""
    result = play(Opponent(), threshold=3)
    assert result.outcome is Outcome.TECHNICAL_LOSS
    assert result.audit is not None
    assert result.audit["result_claim"] == "timeout"


def test_an_opponent_that_has_left_does_not_break_the_reveal() -> None:
    class Gone(Sink):
        def submit_audit(self, payload: dict) -> dict:
            raise ConnectionError("peer already exited")

    result = play(Opponent(turn(1), turn(2)), threshold=2, transport=Gone())
    assert result.audit is not None and verify_audit(result.audit) is True


@pytest.mark.parametrize("bad", [0, -1, True, "35", None])
def test_an_invalid_threshold_is_refused(bad: object) -> None:
    with pytest.raises(TurnLoopError, match="survival_threshold"):
        play(Opponent(turn(1)), threshold=bad)
