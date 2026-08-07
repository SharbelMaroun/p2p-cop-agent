"""`M7-26`: the bundle declares one version, and it is the version this build implements.

Split from `test_artifact_schemas_m7.py`. `X-04` shipped because a bundle bump edited some
`x-contract-version` declarations and not others, leaving a contract nobody could implement
consistently while it still validated its own fixtures.

**The three new artifact schemas joined at 0.2.9 rather than bumping to 0.2.10**, and the
guard is what made that decision visible: it fired immediately on the mismatch. A version
tells a *consumer* something changed, and this bundle is `-proposed` and never accepted
(`M1.5-13`). Bumping would have meant editing 27 declarations across 19 files, several of
them historical narrative of the form "0.2.8 -> 0.2.9" — and rewriting history is how
`X-03` did its damage. The bump belongs to acceptance, not to authoring.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.validate import (
    BUNDLE_CONTRACT_VERSION,
    ArtifactInvalidError,
    check_schema_versions,
    schema_versions,
)

# --- M7-26: a schema change is visible ---------------------------------------------------------


def test_every_controlled_schema_declares_the_same_version() -> None:
    """`X-04` shipped because a bundle bump edited some declarations and not others. This
    caught exactly that on its first run."""
    check_schema_versions()


def test_the_versions_match_the_constant_this_build_implements() -> None:
    for kind, found in schema_versions().items():
        assert found == BUNDLE_CONTRACT_VERSION, f"{kind} declares {found}"


def test_a_partially_bumped_bundle_is_refused() -> None:
    """Proves the guard bites rather than merely existing."""
    with pytest.raises(ArtifactInvalidError, match="disagree"):
        check_schema_versions(expected="9.9.9-nonexistent")
