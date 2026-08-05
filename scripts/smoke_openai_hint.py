"""Live smoke test for the OpenAI hint provider (M6-05, run manually).

Not a CI test -- it makes a real network call and needs a key. Put the key in the gitignored
``.env`` on an ``OPENAI_API_KEY`` line in key/value form (this script loads that file) and run::

    python scripts/smoke_openai_hint.py

Without a key it prints how to set one and exits 0, so it never fails a machine that has none.
The model only phrases the hint; the move is decided in pure Python elsewhere `[AE-25]`.
"""

from __future__ import annotations

import os
from pathlib import Path

from p2p_cop_agent.strategy.verbal import API_KEY_ENV, generate_hint, openai_provider

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def load_dotenv(path: Path) -> None:
    """Set any ``KEY=VALUE`` line from ``.env`` into the environment (no dependency)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, _, value = stripped.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    """Phrase one truthful and one bluffed hint via the live model, or explain the missing key."""
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    if not os.environ.get(API_KEY_ENV):
        print(f"{API_KEY_ENV} is not set. Add it to .env, then re-run. (Zero-token play is default.)")
        return 0
    provider = openai_provider(MODEL)
    for bluff in (False, True):
        hint = generate_hint("the old market square", bluff=bluff, provider=provider)
        print(f"{hint.intent:>5}: {hint.text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
