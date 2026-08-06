"""M6-16: the verbal layer is optional, and a provider outage never costs a turn.

The book makes this a *design guarantee*, not a nicety. The template provider is "the
default. Pre-defined deceptive sentences, **zero tokens**, no network dependency. This is
the **recommended** path as it does not distract from the core algorithm"
(`inst/police_thief_p2p_Summary.md:1565`), and the whole rhetorical layer is offered
"using a free Python template (zero tokens, default), via a local Ollama model, or a
cloud model or CLI" (`:621`).

Rule 25 sits underneath all of it, and is narrower than usually quoted — verbatim at
`:3374` it is a **Recommendation**, not a mandate: "Do not pass the language model the
decision regarding the movement itself; use it for text processing and behavioral profile
generation only. Note: There is no mandatory sanction." We follow it anyway, because an
illegal move *is* sanctioned however it was produced.

What these tests pin is that a team can play the entire league without an account, a
network, or a token — and that a provider failing mid-match is invisible to the opponent
rather than a forfeited turn.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.strategy.hints import BLUFF, TRUTH, HintError, validate_hint
from p2p_cop_agent.strategy.verbal import generate_hint, is_model_turn

SERIES_SUB_GAMES = 6
STEPS_PER_SUB_GAME = 35


def _boom(_place: str, _bluff: bool) -> str:
    raise RuntimeError("provider is down")


def _slow(_place: str, _bluff: bool) -> str:
    raise TimeoutError("provider timed out")


def _junk(_place: str, _bluff: bool) -> object:
    return {"not": "a string"}


def _coordinate_leak(_place: str, _bluff: bool) -> str:
    return "the thief is at 3,4 right now"


def _too_long(_place: str, _bluff: bool) -> str:
    return " ".join(["word"] * 200)


def test_the_default_path_needs_no_provider_at_all() -> None:
    """`:1565`: the template is the default, zero tokens, no network dependency."""
    hint = generate_hint("the park", provider=None)
    assert hint.text
    assert hint.intent in {TRUTH, BLUFF}
    validate_hint(hint.text)  # the floor still passes the guards it imposes on a model


def test_a_full_six_sub_game_series_runs_at_zero_tokens() -> None:
    """`M6-16a` / `[AF-t21]`: a whole counted series is playable without an account.

    Six sub-games of thirty-five steps, no provider anywhere. Every hint is produced,
    valid, and free — which is what makes the league winnable on algorithm quality
    rather than on who is willing to pay for tokens.
    """
    produced = 0
    for _sub_game in range(SERIES_SUB_GAMES):
        for step in range(1, STEPS_PER_SUB_GAME + 1):
            hint = generate_hint(
                "the north edge", provider=None, bluff=(step % 3 == 0), variant=step
            )
            validate_hint(hint.text)
            produced += 1
    assert produced == SERIES_SUB_GAMES * STEPS_PER_SUB_GAME


@pytest.mark.parametrize(
    ("label", "provider"),
    [
        ("a provider that raises", _boom),
        ("a provider that times out", _slow),
        ("a provider returning a non-string", _junk),
        ("a provider leaking coordinates", _coordinate_leak),
        ("a provider exceeding the word limit", _too_long),
    ],
)
def test_a_provider_outage_never_forfeits_the_turn(label: str, provider: object) -> None:
    """`M6-16b`: every failure mode degrades to the template, silently and legally."""
    hint = generate_hint("the harbour", provider=provider)  # type: ignore[arg-type]
    assert hint.text, f"{label} produced no hint"
    validate_hint(hint.text)


def test_the_fallback_is_indistinguishable_from_an_ordinary_hint() -> None:
    """An opponent must not be able to read our outage off the wire.

    A hint that announced its own provenance would leak operational state and hand a
    classmate a signal we never agreed to send.
    """
    healthy = generate_hint("the harbour", provider=None)
    degraded = generate_hint("the harbour", provider=_boom)
    assert degraded.text == healthy.text
    assert degraded.intent == healthy.intent


def test_a_model_can_never_smuggle_a_coordinate_past_the_guard() -> None:
    """`AE-27`: the model passes the same validator the template does, or it is dropped."""
    leaked = generate_hint("the docks", provider=_coordinate_leak)
    assert "3,4" not in leaked.text
    with pytest.raises(HintError):
        validate_hint("the thief is at 3,4 right now")


def test_a_healthy_provider_is_used_when_it_behaves() -> None:
    """The fallback must not be so eager that a working provider never gets a turn."""
    def working(place: str, bluff: bool) -> str:
        return f"circling {place}"

    assert generate_hint("the docks", provider=working).text == "circling the docks"


def test_the_model_is_throttled_to_every_n_steps() -> None:
    """`M6-10f` / `:1581`: `every_n_steps` bounds consumption without breaking play."""
    fired = [step for step in range(1, 13) if is_model_turn(step, 4)]
    assert fired == [4, 8, 12]
    assert all(is_model_turn(step, 1) for step in range(1, 6))  # 1 means every step


def test_a_throttle_of_zero_or_less_disables_the_model_entirely() -> None:
    """Disabling every provider must still produce a complete, legal game (`M6-16`)."""
    assert not any(is_model_turn(step, 0) for step in range(1, 20))
