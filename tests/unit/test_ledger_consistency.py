"""`G-10`..`G-14`: the five planning documents agree with each other, and stay agreeing.

Each of those rows says "keep X consistent", and nothing was keeping them. The invariants
span documents, which is why they went wrong quietly: `PLAN.md` called M6 `DEFERRED` after
all 71 of its tasks closed, and `DOCS_COMPLETENESS.md` was missing 26 rows — while every
line still present in both files was individually correct. There is no single file whose
review catches that.

The tests below run the real checks against the real repository rather than fixtures. A
fixture would prove the parser works on data written to suit it; only this repository can
show the documents are actually consistent right now.
"""

from __future__ import annotations

from scripts.check_ledger_consistency import (
    check_adrs_have_status,
    check_docs_completeness,
    check_plan_matches_todo,
    check_requirements_have_tests,
    check_task_ids_are_unique,
    check_unknowns_are_registered,
    main,
    milestone_states,
    open_milestones,
)


def test_this_repository_is_consistent() -> None:
    """The gate. Its message names the file and the fix, because a failure here is read by
    someone who did not write the inconsistency."""
    assert main() == 0


def test_a_milestone_is_never_done_here_and_open_there() -> None:
    assert check_plan_matches_todo() == []


def test_every_document_is_listed_with_a_status() -> None:
    assert check_docs_completeness() == []


def test_the_remaining_three_checks_are_clean() -> None:
    assert check_requirements_have_tests() == []
    assert check_unknowns_are_registered() == []
    assert check_adrs_have_status() == []


def test_a_prose_state_still_counts_as_open() -> None:
    """**The bug the first parser had.** `M5-07c`'s state is the sentence "BLOCKED — all
    code DONE; needs hardware + M8 evidence". Matching uppercase words left it unmatched,
    unmatched meant uncounted, and M5 read as finished — a checker failing open on the one
    row shaped unlike the others, which is the shape they take."""
    assert "M5" in open_milestones(), (
        "M5-07c is blocked on hardware, so M5 must read as open")


def test_the_parse_is_not_vacuous() -> None:
    """Both sides of the comparison must actually find rows: two empty sets agree."""
    states = milestone_states()
    assert states["M6"] == "DONE"
    assert len(open_milestones()) >= 1

def test_every_milestone_in_the_todo_is_found_in_the_plan() -> None:
    """**The gap this closes.** The plan parser silently dropped two milestones whose state
    cell carried trailing prose after the state word: unmatched meant unchecked, so those
    milestones were never compared at all and the run still reported OK. A checker that
    quietly covers less than it claims is worse than one that fails.
    """
    import re

    from scripts.check_ledger_consistency import read

    in_todo = set(re.findall(r"^\| (M[0-9.]+)-[\w.]+ \|", read("TODO.md"), flags=re.M))
    missing = sorted(in_todo - set(milestone_states()))
    assert not missing, f"PLAN.md states were not parsed for {missing}"

def test_no_task_id_is_used_twice() -> None:
    """**Found by hand, then made permanent.** `M7-22e` named both a closed row and an open
    one, and the open row's status and priority columns were swapped so it read `P1` where
    the status belongs. Anything citing that ID resolved to whichever row the reader found
    first — and the closed one is the one that looks finished."""
    assert check_task_ids_are_unique() == []
