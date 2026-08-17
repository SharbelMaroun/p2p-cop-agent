"""One series identity, computed once and used by every artifact family.

`yanell11` checked their side after we reported ours and found it clean: declaration, all
six configs, all six logs and the result take their uid from a single derivation threaded
through one joining block. Ours did not, and the drift is worth stating plainly because it
is what this module exists to prevent -- friendly-9 wrote **three different identities for
one series**:

    Cop log     41cd0d7dc0f6bbcc0f305f051b9fbbfa       config_sha256[:32], not a UUID
    Thief log   9b80122e-75f9-c32d-5bff-abc032ae086b   the UNLABELLED derivation
    result      248354ae-94b5-0617-238d-cebcf015d984   the agreed value

The result was right because the report layer recomputes it. The logs -- the files an
auditor actually opens -- disagreed with it and with each other. An identity correct in the
aggregate and wrong in the evidence beneath it is worse than an obviously missing one,
because it survives every check that only reads the summary.

`config_sha256[:32]` is the specific mistake worth naming: a value **only this side
computes**, so no peer could reproduce it and no other artifact of ours carried it. The
companion Thief had already replaced it for exactly that reason; the Cop had not.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def shared_game_uid(game_config: Mapping[str, object] | None, game_id: str,
                    groups: Sequence[str], fallback_sha256: str) -> str:
    """Return the uid every artifact of this series must carry.

    Falls back to the legacy `config_sha256[:32]` only when the shared config is absent --
    a caller with no terms cannot derive the real value, and inventing one would be worse
    than the honest old behaviour. Every live path supplies it.
    """
    if not game_config:
        return fallback_sha256[:32]
    from p2p_cop_agent.adapters.report_identity import series_label  # noqa: PLC0415
    from p2p_cop_agent.protocol.negotiation import terms_from_config  # noqa: PLC0415
    from p2p_cop_agent.reporting.series_consensus import derive_game_uid  # noqa: PLC0415

    try:
        terms = terms_from_config(dict(game_config))
        return derive_game_uid(terms, list(groups), series_label(game_id, list(groups)))
    except Exception:  # noqa: BLE001 - a naming problem must not lose a played game's log
        return fallback_sha256[:32]
