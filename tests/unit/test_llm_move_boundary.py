"""`M8-09d`: the language model cannot reach the move decision.

Appendix E rule 25 is a **Recommendation**, not a Mandatory rule, and the book says so
explicitly: "Recommendation not to transfer the decision on the movement move itself to the
language model. It is better to use it for creating a behavioural profile and for producing
text only. **Note: there is no mandatory sanction**, but blind reliance may lead to logical
malfunctions and a technical loss" (p.130/273).

So this is not a rule with a penalty attached — which makes it *more* worth proving
structurally, not less. The penalty arrives indirectly and expensively: a hallucinated move
is an **illegal** move, and rule 13's sanction for that is "illegal move and technical
loss", scored 0/0 under Table 2. A recommendation whose violation costs the game is the
kind of thing a grader probes and a team assumes.

**"We do not do that" is not an answer.** The reference makes the same guarantee two ways,
and both are worth copying: no move-deciding module can *see* the language layer, and the
move is chosen **before** the model is called at all. This module asserts the first as a
transitive import closure — the second is an ordering property of the turn loop and is
asserted in `test_failure_matrix.py`.

What the LLM *is* allowed to do is unchanged: produce hints and behavioural profiling. The
opponent's hint reaching our trust model is also fine — consuming the verbal channel is the
game. What may not happen is our own text generator choosing our own move.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from p2p_cop_agent.strategy import barrier_policy, belief_pursuit, pursuit, squeeze

SRC = Path(__file__).resolve().parents[2] / "src" / "p2p_cop_agent"

# Everything that turns state into a move or a barrier. If a module here could reach the
# language layer, rule 25's recommendation would be one import away from being violated.
MOVE_DECIDERS = ("strategy/pursuit.py", "strategy/belief_pursuit.py",
                 "strategy/squeeze.py", "strategy/barrier_policy.py",
                 "strategy/belief.py")

# The language layer and everything that carries free text into it.
LANGUAGE_LAYER = ("strategy.verbal", "strategy.hints", "strategy.hint_decode",
                  "strategy.hint_consumption", "strategy.landmarks", "strategy.trust",
                  "strategy.consume", "llm", "adapters.serve")


def _imports(relative: str) -> set[str]:
    tree = ast.parse((SRC / relative).read_text("utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
    return found


def _closure(relative: str, seen: set[str] | None = None) -> set[str]:
    """Every module a decider reaches, transitively.

    Direct imports are the easy half. The failure this guards against is indirect: a
    pursuit module importing a helper that imports the hint decoder, at which point the
    boundary is gone and no single file looks wrong.
    """
    seen = set() if seen is None else seen
    for module in _imports(relative):
        if not module.startswith("p2p_cop_agent") or module in seen:
            continue
        seen.add(module)
        path = SRC / (module.removeprefix("p2p_cop_agent.").replace(".", "/") + ".py")
        if path.exists():
            _closure(str(path.relative_to(SRC)).replace("\\", "/"), seen)
    return seen


@pytest.mark.parametrize("decider", MOVE_DECIDERS)
def test_no_move_deciding_module_can_reach_the_language_layer(decider: str) -> None:
    """**The test this module exists for.** Transitive, so an indirect route fails too."""
    reached = _closure(decider)
    leaked = sorted(m for m in reached if any(part in m for part in LANGUAGE_LAYER))
    assert not leaked, (
        f"{decider} reaches the language layer via {leaked}; rule 25 recommends the move "
        "decision stay algorithmic, and a hallucinated move is an illegal move [AE-13]"
    )


@pytest.mark.parametrize(
    "function",
    [pursuit.choose_action, belief_pursuit.pursue_belief,
     belief_pursuit.belief_turn_intent, squeeze.choose_squeeze,
     barrier_policy.choose_turn_intent],
)
def test_no_move_function_accepts_free_text(function) -> None:
    """A second, independent check: even with the imports clean, a caller could hand a
    decider a string it had generated. No move function takes one — the arguments are a
    board, a position, a belief and a barrier set, and nothing that could carry a sentence.
    """
    hints = inspect.get_annotations(function, eval_str=False)
    # `\bstr\b`, not `"str" in ...`: the substring version flagged `AbstractSet[Coordinate]`
    # because "Ab**str**actSet" contains it. A guard that cries wolf on a set of coordinates
    # is a guard someone deletes.
    suspicious = {name: annotation for name, annotation in hints.items()
                  if name != "return" and re.search(r"\bstr\b", str(annotation))}
    assert not suspicious, f"{function.__name__} accepts free text: {suspicious}"


def test_the_language_layer_does_exist_so_this_is_not_vacuous() -> None:
    """A boundary test passes trivially if there is nothing on the other side. There is:
    the verbal layer is real, tested, and used — just not by the deciders."""
    assert (SRC / "strategy" / "verbal.py").exists()
    assert _imports("strategy/verbal.py"), "verbal.py imports nothing; is it a stub?"


def test_the_hint_path_reaches_trust_but_trust_never_reaches_a_decider() -> None:
    """The permitted direction, stated so nobody 'fixes' it. Consuming the opponent's hint
    is the game — `:1660`'s trust map is built from it. What must not happen is that trust,
    or anything downstream of free text, feeds the move choice."""
    assert any("hint" in module for module in _closure("strategy/trust.py"))
    for decider in MOVE_DECIDERS:
        assert "p2p_cop_agent.strategy.trust" not in _closure(decider), decider
