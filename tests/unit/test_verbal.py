"""M6-05 / M6-10f: the optional LLM adapter always degrades to the zero-token template.

The model only phrases; it never moves (`AE-25`). Every provider failure -- absent, raising,
timing out, empty, over-long, or coordinate-laden -- must become the deterministic template,
so a turn never stalls and an illegal hint is never emitted. All offline: providers are fakes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p2p_cop_agent.strategy.hints import BLUFF, TRUTH, Hint, encodes_coordinates, within_word_limit
from p2p_cop_agent.strategy.verbal import (
    API_KEY_ENV,
    HintProviderError,
    generate_hint,
    is_model_turn,
    openai_provider,
    provider_from_config,
)


def test_no_provider_uses_the_zero_token_template() -> None:
    hint = generate_hint("old market", provider=None)
    assert isinstance(hint, Hint)
    assert hint.intent == TRUTH
    assert "old market" in hint.text


def test_a_good_provider_output_is_returned_with_its_intent() -> None:
    hint = generate_hint("river", bluff=True, provider=lambda p, b: "way off past the docks")
    assert hint.text == "way off past the docks"
    assert hint.intent == BLUFF


def _raises(_place: str, _bluff: bool) -> str:
    raise RuntimeError("provider down")


@pytest.mark.parametrize("provider", [
    _raises,
    lambda p, b: "meet at 3,4",          # coordinate channel -> rejected
    lambda p, b: "w " * 30,               # over the word limit
    lambda p, b: "   ",                    # empty after strip
    lambda p, b: None,                     # non-string -> .strip() raises
])
def test_any_bad_provider_falls_back_to_the_template(provider: object) -> None:
    hint = generate_hint("park", provider=provider)  # type: ignore[arg-type]
    assert isinstance(hint, Hint)
    assert within_word_limit(hint.text, 15) and not encodes_coordinates(hint.text)
    assert "park" in hint.text  # the template phrased it, not the failing provider


def test_the_model_can_never_smuggle_coordinates_past_the_guard() -> None:
    hint = generate_hint("dock 7", provider=lambda p, b: "target at row 4 col 9")
    assert not encodes_coordinates(hint.text)


def _fake_transport(payload: str):
    return lambda url, data, headers, timeout: json.dumps(payload).encode()


def test_openai_provider_builds_and_parses_a_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, "sk-test")
    body = {"choices": [{"message": {"content": "closing in near the old bridge"}}]}
    provider = openai_provider("gpt-4o-mini", transport=_fake_transport(body))
    assert generate_hint("old bridge", provider=provider).text == "closing in near the old bridge"


def test_openai_provider_without_a_key_degrades_to_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    provider = openai_provider("gpt-4o-mini", transport=_fake_transport({}))
    hint = generate_hint("harbour", provider=provider)
    assert "harbour" in hint.text  # template, because the key was absent


@pytest.mark.parametrize("step,every_n,expected", [
    (0, 3, True), (1, 3, False), (2, 3, False), (3, 3, True), (5, 1, True), (4, 0, False),
])
def test_is_model_turn_throttles_the_provider(step: int, every_n: int, expected: bool) -> None:
    assert is_model_turn(step, every_n) is expected


def test_config_selects_template_by_default() -> None:
    assert provider_from_config({}) is None
    assert provider_from_config({"trash_talk": {"provider": "template"}}) is None


def test_config_builds_the_openai_provider() -> None:
    cfg = {"trash_talk": {"provider": "openai"}, "llm": {"model": "gpt-4o-mini"}}
    assert callable(provider_from_config(cfg, transport=_fake_transport({})))


def test_config_rejects_openai_without_a_model() -> None:
    with pytest.raises(HintProviderError, match="model"):
        provider_from_config({"trash_talk": {"provider": "openai"}})


@pytest.mark.parametrize("name", ["ollama", "claude_api", "claude_cli", "bogus"])
def test_config_rejects_an_unbuilt_provider_loudly(name: str) -> None:
    with pytest.raises(HintProviderError):
        provider_from_config({"trash_talk": {"provider": name}})


def test_movement_never_imports_the_verbal_layer() -> None:
    """M6-05d structurally: no move-deciding module can reach the LLM."""
    strategy_dir = Path(__file__).resolve().parents[2] / "src" / "p2p_cop_agent" / "strategy"
    for module in ("pursuit.py", "belief_pursuit.py", "barrier_policy.py"):
        source = (strategy_dir / module).read_text(encoding="utf-8")
        assert "verbal" not in source and "openai" not in source
