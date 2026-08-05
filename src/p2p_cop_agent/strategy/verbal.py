"""Optional verbal/LLM adapter with a guaranteed zero-token fallback (M6-05, M6-10f).

The template layer (:mod:`p2p_cop_agent.strategy.hints`) is the always-available floor: a
whole series is playable at zero tokens `[AF-t21]`. This module makes the LLM an *optional*
provider on top, bound by one iron rule -- **the model only ever phrases a hint, it never
chooses a move** `[AE-25]` `[ADR-007]`. A provider is a plain callable ``(place, bluff) ->
text``; it returns natural language and may fail however it likes, because
:func:`generate_hint` turns *any* failure into the deterministic template:

* provider is ``None`` (the ``template`` default) -> template;
* provider raises, times out, or returns a non-string -> template (M6-05e -- a blocked
  provider never stalls a turn);
* provider returns text that breaks the word limit or the no-coordinate rule -> template
  (the model cannot bypass the guard that the template also passes, M6-05c/d).

So the emitted hint is *always* valid and a turn *never* hangs on the network. The OpenAI
provider reads its key from the environment at runtime and injects its transport, so the
request-building and response-parsing are tested offline and a missing key degrades to
zero-token play rather than crashing. Selection is config-driven: ``[trash_talk].provider``
picks the provider, ``[llm].model`` names the model.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable, Mapping

from p2p_cop_agent.strategy.hints import (
    BLUFF,
    HINT_MAX_WORDS_DEFAULT,
    TRUTH,
    Hint,
    HintError,
    template_hint,
    validate_hint,
)

# A provider phrases a hint; it never decides a move (AE-25). Any failure becomes the template.
HintProvider = Callable[[str, bool], str]

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_TIMEOUT_S = 30.0
API_KEY_ENV = "OPENAI_API_KEY"

_SYSTEM_PROMPT = (
    "You phrase one short taunt for a pursuit game. Output a single natural-language clue, "
    "at most 15 words, with no numbers, no coordinates, and no row, column, or cell "
    "references."
)


class HintProviderError(RuntimeError):
    """Raised at setup for a configured provider that cannot be built."""


def generate_hint(
    place: str,
    *,
    bluff: bool = False,
    provider: HintProvider | None = None,
    variant: int = 0,
    max_words: int = HINT_MAX_WORDS_DEFAULT,
) -> Hint:
    """Return a validated :class:`Hint`, falling back to the template on any provider failure."""

    def _template() -> Hint:
        return template_hint(place, bluff=bluff, variant=variant, max_words=max_words)

    if provider is None:
        return _template()
    try:
        text = provider(place, bluff).strip()
        if not text:
            raise HintError("provider returned an empty hint")
        validated = validate_hint(text, max_words)
    except Exception:  # noqa: BLE001 -- any provider failure degrades to zero-token play
        return _template()
    return Hint(validated, BLUFF if bluff else TRUTH)


def is_model_turn(step: int, every_n: int) -> bool:
    """Return whether the model runs on this step; other steps use the template (M6-10f).

    A non-positive cadence disables the model entirely, so ``every_n = 0`` is zero-token play.
    """
    return every_n > 0 and step % every_n == 0


def _build_messages(place: str, bluff: bool) -> list[dict[str, str]]:
    """Return the chat messages asking for a truthful or misleading clue about ``place``."""
    aim = "a misleading" if bluff else "a truthful"
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"Give {aim} clue about the target being near '{place}'."},
    ]


def _http_post(url: str, data: bytes, headers: dict[str, str], timeout: float) -> bytes:  # pragma: no cover -- network I/O, runbook-only
    """POST ``data`` and return the raw response body (the one real network touch)."""
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 -- fixed https endpoint
        return response.read()


def openai_provider(
    model: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_S,
    api_key_env: str = API_KEY_ENV,
    transport: Callable[[str, bytes, dict[str, str], float], bytes] = _http_post,
) -> HintProvider:
    """Return a provider that phrases a hint via the OpenAI chat API.

    The key is read from ``api_key_env`` at call time -- a missing key raises, which
    :func:`generate_hint` turns into the template, so an unconfigured key is a graceful
    downgrade, not a crash. ``transport`` is injected so parsing is testable without a network.
    """

    def _call(place: str, bluff: bool) -> str:
        key = os.environ.get(api_key_env)
        if not key:
            raise HintProviderError(f"{api_key_env} is not set")
        body = json.dumps(
            {"model": model, "messages": _build_messages(place, bluff), "max_tokens": 40}
        ).encode("utf-8")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = json.loads(transport(OPENAI_ENDPOINT, body, headers, timeout))
        return payload["choices"][0]["message"]["content"]

    return _call


def provider_from_config(
    game_config: Mapping[str, object],
    *,
    transport: Callable[[str, bytes, dict[str, str], float], bytes] = _http_post,
) -> HintProvider | None:
    """Build the configured hint provider, or ``None`` for the zero-token template default.

    Reads ``[trash_talk].provider`` and ``[llm].model``. ``template`` (the default) returns
    ``None``; ``openai`` returns the adapter. A recognised-but-unbuilt provider
    (``ollama``/``claude_api``/``claude_cli``) or an unknown name raises here, so a
    misconfiguration is loud at setup rather than a silent downgrade at play time.
    """
    trash_talk = game_config.get("trash_talk")
    name = trash_talk.get("provider", "template") if isinstance(trash_talk, Mapping) else "template"
    if name == "template":
        return None
    if name == "openai":
        llm = game_config.get("llm")
        model = llm.get("model") if isinstance(llm, Mapping) else None
        if not isinstance(model, str) or not model:
            raise HintProviderError("the openai provider requires [llm].model")
        deadline = llm.get("step_deadline_seconds", DEFAULT_TIMEOUT_S)
        timeout = float(deadline) if isinstance(deadline, int | float) else DEFAULT_TIMEOUT_S
        return openai_provider(model, timeout=timeout, transport=transport)
    raise HintProviderError(f"hint provider {name!r} is not implemented")
