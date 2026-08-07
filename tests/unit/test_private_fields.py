"""`M8-09b`: a leakage vector per private field class, per channel.

The row's condition is literally "leakage vector per private field class", so there is one
test per class — each planting a realistic value and asserting the guard catches it. Rule 2
(Prohibited) sanctions data leakage with **immediate disqualification**, which is why the
guard raises rather than quietly stripping the field: silently sanitising would hide the
bug that put it there and ship the next one.

The interesting half is the *permitted* disclosures. `llm_model` and `mcp_servers` are
private classes that the declaration is **required** to carry, so a guard that refused them
would break a mandatory artifact. Those are tested too, because a boundary is only correct
if it lets the legal case through.
"""

from __future__ import annotations

import pytest

from p2p_cop_agent.protocol.private_fields import (
    CHANNEL_DISCLOSURES,
    PRIVATE_FIELD_CLASSES,
    PrivateFieldLeakError,
    check_outbound,
    private_fields_in,
)

# One realistic leak per class, as it would actually appear in a config.
# A key-SHAPED value that is not a key. Named with a marker the secret scanner already
# recognises as a placeholder, because the scanner is right to flag a credential-looking
# literal next to `api_key` and silencing it with an allowlist entry would weaken it for
# every future file.
PLACEHOLDER_KEY = "sk-placeholder-" + "0" * 12
PLACEHOLDER_TOKEN = "placeholder-refresh-token"

VECTORS = {
    "network": {"my_port": 8801},
    "strategy": {"police_class": "GreedyPursuit", "seed": 1234},
    "llm": {"provider": "claude_api", "api_key": PLACEHOLDER_KEY},
    "language": {"trash_talk": {"banter": True}},
    "contact": {"recipient": "someone@example.com"},
    "credential": {"refresh_token": PLACEHOLDER_TOKEN},
}


@pytest.mark.parametrize("field_class", sorted(PRIVATE_FIELD_CLASSES))
def test_each_private_field_class_is_caught_in_the_shared_config(field_class: str) -> None:
    """**The row's own condition.** The signed terms are held byte-identically by both
    sides (rule 11), so a private value here is one side's local truth inside a document
    the opponent also signs."""
    leaks = private_fields_in(VECTORS[field_class], "shared_config")
    assert leaks, f"no vector detected for the {field_class} class"
    assert all(leak.startswith(f"{field_class}:") for leak in leaks), leaks


@pytest.mark.parametrize("field_class", sorted(PRIVATE_FIELD_CLASSES))
def test_each_private_field_class_is_caught_in_a_turn_message(field_class: str) -> None:
    """A turn carries a digest, then a move and a hint. Nothing from the private file has
    any business riding along, and a turn crosses the wire far more often than a config."""
    turn = {"step": 3, "sender": "police", "commit": "a" * 64, **VECTORS[field_class]}
    assert private_fields_in(turn, "turn"), f"{field_class} rode a turn message unnoticed"


def test_a_leak_nested_several_levels_deep_is_still_found() -> None:
    """The realistic shape. Nobody puts an API key at the top level of a message; it
    arrives inside an identity block inside a payload."""
    document = {"payload": {"identity": {"llm": {"api_key": PLACEHOLDER_KEY}}}}
    leaks = private_fields_in(document, "shared_config")
    assert "llm:payload.identity.llm" in leaks or any("api_key" in leak for leak in leaks)


def test_a_leak_inside_a_list_is_found() -> None:
    """Groups arrive as a list, so a per-group leak is a list element."""
    document = {"groups": [{"group_id": "a"}, {"group_id": "b", "seed": 99}]}
    assert private_fields_in(document, "shared_config"), "a leak in list position 1 escaped"


# --- the permitted disclosures, which are the harder half --------------------------------


def test_the_declaration_may_carry_the_model_name_and_the_mcp_urls() -> None:
    """Asked directly: the declaration must disclose `llm_model` and `mcp_servers`. A guard
    that refused them would break a **mandatory** artifact (rule 24, `:2229`), which is why
    the rule is per channel rather than global."""
    group = {"group_id": "sharNamr", "llm_model": "template-free",
             "mcp_servers": {"peer": "https://x.example.com/mcp"},
             "repos": {"cop": "https://github.com/x/cop"}}
    check_outbound({"groups": [group]}, "declaration")


def test_the_same_declaration_content_is_refused_in_the_shared_config() -> None:
    """The contrast that proves the channels are actually distinct rather than decorative."""
    group = {"llm_model": "template-free", "mcp_servers": {"peer": "https://x/mcp"}}
    check_outbound({"groups": [group]}, "declaration")
    with pytest.raises(PrivateFieldLeakError, match="private field"):
        check_outbound({"groups": [group]}, "shared_config")


def test_the_declaration_still_refuses_the_provider_behind_the_model() -> None:
    """The fine distinction, and the one worth having: the declaration says **which model**,
    never **how we reach it**. `llm_model` is disclosed; `provider` and `api_key` are not."""
    with pytest.raises(PrivateFieldLeakError, match="llm:"):
        check_outbound({"llm_model": "haiku", "provider": "claude_api"}, "declaration")


def test_repository_links_are_published_by_design_and_need_no_disclosure() -> None:
    """Rule 49 requires four repository links in the artifacts, and `:2901` does not list
    repositories among the private values — group identity is published, not hidden. So
    `repos` appears in no private class, and allow-listing it would have said something
    false about it."""
    links = {"groups": [{"repos": {"cop": "https://a", "thief": "https://b"}}]}
    for channel in ("result", "declaration", "shared_config"):
        check_outbound(links, channel)


def test_an_mcp_url_containing_a_port_is_not_flagged_as_a_port_leak() -> None:
    """Matching on keys rather than values. The required `mcp_servers` URL contains a port
    by construction, so a value-matching guard would refuse the mandatory disclosure."""
    check_outbound({"mcp_servers": {"peer": "http://127.0.0.1:8801/mcp"}}, "declaration")


# --- the guard's own failure modes -------------------------------------------------------


def test_an_unknown_channel_is_refused_rather_than_defaulted() -> None:
    """Defaulting permissive ships a channel unguarded; defaulting strict drops a mandatory
    field. Refusing makes a new message type declare itself."""
    with pytest.raises(PrivateFieldLeakError, match="unknown channel"):
        private_fields_in({"anything": 1}, "gossip")


def test_a_clean_document_passes_every_channel() -> None:
    """A guard that refused everything would pass every leak test and block every match."""
    clean = {"step": 1, "sender": "police", "commit": "a" * 64, "hint": "near the park"}
    for channel in CHANNEL_DISCLOSURES:
        check_outbound(clean, channel)


def test_the_error_names_the_class_and_the_path() -> None:
    """An operator needs to know *what kind* of thing escaped and *where* it sat."""
    with pytest.raises(PrivateFieldLeakError) as caught:
        check_outbound({"identity": {"seed": 7}}, "turn")
    assert "strategy:identity.seed" in str(caught.value)
    assert "AE-2" in str(caught.value)
