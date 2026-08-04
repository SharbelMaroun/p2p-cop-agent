"""The verbal layer: zero-token hint generation, bounded and coordinate-free (M6-05, M6-10).

Every turn a peer may send a natural-language hint, truthful or bluffed. Two book rules
are hard constraints applied to **every** provider -- the zero-token template here and
any future LLM alike:

* the hint must stay within the negotiated word limit (``world.hint_max_words``, default
  15) `[AF-t14]` (M6-05b, M6-10c);
* the hint must be natural language with **no coordinate or numeric protocol** `[AE-26]`
  `[AE-27]` -- a covert channel that leaks position is a disqualification, so a validator
  refuses it rather than trusting a convention (M6-05c, M6-10d).

The intent (truth vs bluff) is an explicit flag carried into the sealed commitment so it
cannot be revised after the fact (M6-10a). The default provider is a **template** that
needs no network and no account, so a whole series is playable at zero tokens `[AF-t21]`
(M6-05a, M6-10b); the LLM never chooses a move `[AE-25]`, only phrases a hint.

The coordinate validator is deliberately conservative (PROJECT-PROPOSED): it refuses a
digit *pair* (``3,4`` / ``3 4``) and an explicit ``row``/``col``/``cell`` index, while
allowing worded quantities (``three blocks north``). Our own templates emit no digits.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

HINT_MAX_WORDS_DEFAULT = 15
TRUTH = "truth"
BLUFF = "bluff"

_COORD_PAIR = re.compile(r"\d+\s*[,; ]\s*\d+")
_COORD_LABEL = re.compile(r"\b(?:rows?|cols?|columns?|cells?|coord\w*)\b\s*\d+", re.IGNORECASE)

_TRUTH_TEMPLATES = ("closing in near the {p}", "heading toward the {p}", "somewhere by the {p}")
_BLUFF_TEMPLATES = ("nowhere near the {p}", "far from the {p}", "way past the {p}")


class HintError(ValueError):
    """Raised when a hint breaks the word limit or the no-coordinate rule."""


@dataclass(frozen=True, slots=True)
class Hint:
    """A natural-language hint and its sealed truth/bluff intent."""

    text: str
    intent: str


def hint_max_words(game_config: Mapping[str, object]) -> int:
    """Return the negotiated hint word limit, or the 15-word default."""
    world = game_config.get("world")
    if isinstance(world, Mapping):
        value = world.get("hint_max_words")
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            return value
    return HINT_MAX_WORDS_DEFAULT


def within_word_limit(text: str, max_words: int = HINT_MAX_WORDS_DEFAULT) -> bool:
    """Return whether ``text`` is at or under the word limit."""
    return len(text.split()) <= max_words


def enforce_word_limit(text: str, max_words: int = HINT_MAX_WORDS_DEFAULT) -> str:
    """Return ``text`` truncated to at most ``max_words`` words."""
    return " ".join(text.split()[:max_words])


def encodes_coordinates(text: str) -> bool:
    """Return whether ``text`` carries a coordinate or numeric location protocol `[AE-27]`."""
    return bool(_COORD_PAIR.search(text) or _COORD_LABEL.search(text))


def validate_hint(text: str, max_words: int = HINT_MAX_WORDS_DEFAULT) -> str:
    """Return ``text`` if it is within the limit and coordinate-free, else raise.

    Applied to the template and to any model output alike -- the rule is the hint's,
    not the provider's.
    """
    if not within_word_limit(text, max_words):
        raise HintError(f"hint exceeds {max_words} words: {text!r}")
    if encodes_coordinates(text):
        raise HintError(f"hint encodes coordinates (AE-27 forbids numeric protocols): {text!r}")
    return text


def template_hint(
    place: str,
    *,
    bluff: bool = False,
    variant: int = 0,
    max_words: int = HINT_MAX_WORDS_DEFAULT,
) -> Hint:
    """Return a zero-token templated hint about ``place`` with its intent flag.

    ``place`` is a natural-language descriptor (a landmark or bearing word), never a
    coordinate; the result is truncated to the limit and validated, so a bad ``place``
    (one carrying digits) is refused rather than emitted.
    """
    templates = _BLUFF_TEMPLATES if bluff else _TRUTH_TEMPLATES
    text = enforce_word_limit(templates[variant % len(templates)].format(p=place), max_words)
    validate_hint(text, max_words)
    return Hint(text, BLUFF if bluff else TRUTH)
