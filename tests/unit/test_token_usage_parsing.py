"""`M7-11`: reading token usage off a provider response.

Split from `test_token_ledger.py`, which covers the accounting. This covers where the
numbers come from — the place a correct ledger still reports a wrong figure, because a
provider that stopped returning usage looks exactly like a game that used no tokens.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.reporting.token_ledger import TokenLedgerError, usage_from_response


@pytest.mark.parametrize(("prompt_key", "completion_key"),
                         [("prompt_tokens", "completion_tokens"),
                          ("input_tokens", "output_tokens")])
def test_usage_is_read_from_either_provider_naming(prompt_key, completion_key) -> None:
    """Two providers, two names for the same number. Supporting one silently reports zero
    for the other."""
    assert usage_from_response({"usage": {prompt_key: 10, completion_key: 5}}).total == 15


def test_a_response_with_no_usage_block_is_refused() -> None:
    """**A provider that stopped returning usage looks exactly like a game that used no
    tokens**, and the second is a figure we would report to the league as fact."""
    with pytest.raises(TokenLedgerError, match="AE-54"):
        usage_from_response({"choices": []})


@pytest.mark.parametrize("broken", [{"prompt_tokens": "many", "completion_tokens": 5},
                                    {"prompt_tokens": 5}, {}])
def test_a_usage_block_without_integer_counts_is_refused(broken: dict) -> None:
    """A partial block is the shape a provider change takes — one field renamed, the other
    left alone — and reading the survivor alone halves the reported figure."""
    with pytest.raises(TokenLedgerError, match="no integer token counts"):
        usage_from_response({"usage": broken})


def test_a_negative_count_and_a_non_positive_limit_are_refused() -> None:
    """Both constructors fail closed. A negative count would make the series total smaller
    than one of its parts, and a zero limit would mark every game an over-run."""
    from p2p_cop_agent.reporting.token_ledger import TokenLedger, TokenUsage  # noqa: PLC0415

    with pytest.raises(TokenLedgerError, match="cannot be negative"):
        TokenUsage(prompt=-1, completion=0)
    with pytest.raises(TokenLedgerError, match="must be positive"):
        TokenLedger(max_tokens_per_game=0)
