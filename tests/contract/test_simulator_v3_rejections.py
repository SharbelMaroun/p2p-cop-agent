"""Rejection conformance for the simulator-v3.0.0 compatibility profile.

Split from ``test_simulator_v3_compatibility.py`` (which holds the positive
golden cases) so each file stays within the test file-length limit.
"""

from copy import deepcopy
from pathlib import Path

import pytest

from p2p_cop_agent.protocol import ProtocolError, validate_message
from p2p_cop_agent.shared.config import load_json_object

WIRE_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "shared_contract"
    / "fixtures"
    / "simulator-v3.0.0-wire.golden.json"
)


def messages() -> dict:
    """Return the golden wire messages by fixture name."""
    return load_json_object(WIRE_FIXTURE)["messages"]  # type: ignore[return-value]


@pytest.mark.parametrize(
    ("logical_name", "fixture_name", "path", "wrong_value"),
    [
        pytest.param(
            "negotiate",
            "negotiation",
            ("terms",),
            {"grid_size": 7, "max_moves": 35},
            id="legacy-negotiation-term-names",
        ),
        pytest.param(
            "negotiate",
            "negotiation",
            ("signature",),
            "not-a-sha256-digest",
            id="malformed-negotiation-signature",
        ),
        pytest.param(
            "negotiate",
            "negotiation",
            ("identity", "members"),
            "member-001",
            id="identity-members-not-array",
        ),
        pytest.param(
            "turn",
            "normal_turn",
            ("smell_grid",),
            [[0.9]],
            id="matrix-smell-grid",
        ),
        pytest.param(
            "turn",
            "capture_claim_turn",
            ("barrier_placed",),
            True,
            id="boolean-barrier",
        ),
        pytest.param(
            "turn",
            "capture_claim_turn",
            ("capture_claim",),
            False,
            id="boolean-capture-claim",
        ),
        pytest.param(
            "turn",
            "claim_response_turn",
            ("claim_response",),
            [],
            id="array-claim-response",
        ),
        pytest.param(
            "turn",
            "win_claim_turn",
            ("win_claim",),
            True,
            id="boolean-win-claim",
        ),
        pytest.param(
            "turn",
            "normal_turn",
            ("move",),
            "N",
            id="private-move-leak",
        ),
        pytest.param(
            "audit",
            "audit_payload",
            ("result_claim",),
            {"outcome": "capture"},
            id="object-audit-result",
        ),
        pytest.param(
            "audit",
            "audit_payload",
            ("result_claim",),
            "survived",
            id="unknown-audit-result",
        ),
        pytest.param(
            "audit",
            "audit_payload",
            ("records",),
            [{"payload": {"step": 1}, "nonce": "0" * 32}],
            id="audit-record-without-commit",
        ),
    ],
)
def test_cop_rejects_important_wrong_wire_shapes(
    logical_name: str,
    fixture_name: str,
    path: tuple[str, ...],
    wrong_value: object,
) -> None:
    candidate = deepcopy(messages()[fixture_name])
    target = candidate
    for field in path[:-1]:
        target = target[field]
    target[path[-1]] = wrong_value

    with pytest.raises(ProtocolError):
        validate_message(logical_name, candidate)
