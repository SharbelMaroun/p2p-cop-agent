"""M5-08b: no subsystem references another directly.

Appendix E rule 3 wires the five subsystems only through the coordinator. This
walks each subsystem's source and asserts it imports none of its siblings -- a
direct peer link would let two subsystems bypass the gateway, which is exactly the
coupling rule 3 forbids. Shared, sub-subsystem infrastructure (reading a signed
match limit) lives in `services.limits`, which is not a subsystem and is allowed;
that neutral module is what let the watchdog stop importing the deadline tracker.
"""

from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_cop_agent"

# subsystem name -> its source files
SUBSYSTEMS = {
    "connector": ["adapters/fastmcp_client.py", "adapters/fastmcp_server.py"],
    "decision": ["strategy/pursuit.py", "strategy/barrier_policy.py"],
    "deadline_tracker": ["services/deadlines.py"],
    "watchdog": ["services/watchdog.py"],
}
# the import fragment that betrays each subsystem
SIGNATURE = {
    "connector": "adapters",
    "decision": "strategy",
    "deadline_tracker": "services.deadlines",
    "watchdog": "services.watchdog",
}


def _source(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", list(SUBSYSTEMS))
def test_a_subsystem_imports_no_sibling(name: str) -> None:
    forbidden = {sig for other, sig in SIGNATURE.items() if other != name}
    for rel in SUBSYSTEMS[name]:
        source = _source(rel)
        for fragment in forbidden:
            assert f"p2p_cop_agent.{fragment}" not in source, (
                f"{rel} imports sibling subsystem {fragment}"
            )


def test_no_subsystem_imports_the_gateway() -> None:
    """The dependency points one way: the gateway knows the subsystems, never the
    reverse, so a subsystem cannot reach up and drive the coordinator."""
    for files in SUBSYSTEMS.values():
        for rel in files:
            source = _source(rel)
            assert "orchestration.orchestrator" not in source
            assert "orchestration.ports" not in source


def test_the_gateway_depends_on_ports_not_concrete_subsystems() -> None:
    """The coordinator wires interfaces: it imports none of the four concrete
    subsystem modules, so a subsystem can be swapped without touching it."""
    source = _source("orchestration/orchestrator.py")
    for fragment in SIGNATURE.values():
        assert f"p2p_cop_agent.{fragment}" not in source
