"""A tiny explicit-state model checker (Chapter 5).

A *model* describes a system as a state machine:

* ``initial_states()`` returns the states the system may start in;
* ``next_states(state)`` returns every possible next step as
  ``(action_name, new_state)`` pairs;
* ``invariants`` maps a name to a predicate that must be true in *every*
  reachable state.

The checker explores every reachable state by breadth-first search (BFS).
States must be immutable and hashable (tuples, frozensets, frozen
dataclasses), so the checker can remember which ones it has already seen in
a set and never explores a state twice. Because BFS visits states in order
of distance from the start, the first invariant violation it finds has the
*shortest* possible counterexample trace.

This is the same idea as TLC, the model checker for TLA+, stripped to its
core. Only safety properties ("nothing bad ever happens") are checked;
liveness ("something good eventually happens") is out of scope.

Run ``python3 models.py`` to check every bundled model.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, Tuple

State = Hashable
Step = Tuple[str, State]


@dataclass(frozen=True)
class Model:
    """A system to check. See the module docstring for the three parts."""

    name: str
    initial_states: Callable[[], Iterable[State]]
    next_states: Callable[[State], Iterable[Step]]
    invariants: Dict[str, Callable[[State], bool]]
    describe: Callable[[State], str] = repr
    """Turns a state into a short human-readable line for traces."""


@dataclass
class Result:
    """What the checker found."""

    model: str
    ok: bool
    states: int = 0
    """Distinct reachable states discovered (the size of the seen set)."""
    transitions: int = 0
    """Successor edges examined, including ones leading to seen states."""
    depth: int = 0
    """Length of the longest shortest path from an initial state."""
    terminal_states: int = 0
    """States with no successors (finished or deadlocked)."""
    violated: Optional[str] = None
    """Name of the first invariant found false, if any."""
    trace: List[Step] = field(default_factory=list)
    """Shortest path to the violating state: ``("Init", s0), (action, s1), ...``"""
    truncated: bool = False
    """True when ``max_states`` stopped the search before it finished."""

    def summary(self) -> str:
        verdict = "PASS" if self.ok else f"FAIL: invariant {self.violated!r} violated"
        if self.truncated:
            verdict += " (search truncated)"
        return (f"{self.model}: {verdict}; {self.states} states, "
                f"{self.transitions} transitions, depth {self.depth}")


def check(model: Model, max_states: Optional[int] = None) -> Result:
    """Explore every reachable state of ``model`` breadth-first.

    Stops at the first invariant violation and returns the shortest trace to
    it. ``max_states`` bounds the search for models whose state space is too
    large (the result is then marked ``truncated``).
    """
    result = Result(model=model.name, ok=True)
    # parent[s] = (previous state, action) lets us rebuild the path to s.
    parent: Dict[State, Optional[Tuple[State, str]]] = {}
    depth: Dict[State, int] = {}
    frontier: deque = deque()

    def violated(state: State) -> Optional[str]:
        for name, predicate in model.invariants.items():
            if not predicate(state):
                return name
        return None

    def fail(state: State, name: str) -> Result:
        result.ok = False
        result.violated = name
        result.trace = _trace(parent, state)
        result.states = len(parent)
        return result

    for s0 in model.initial_states():
        if s0 in parent:
            continue
        parent[s0] = None
        depth[s0] = 0
        bad = violated(s0)
        if bad:
            return fail(s0, bad)
        frontier.append(s0)

    while frontier:
        state = frontier.popleft()
        successors = list(model.next_states(state))
        if not successors:
            result.terminal_states += 1
        for action, nxt in successors:
            result.transitions += 1
            if nxt in parent:
                continue
            parent[nxt] = (state, action)
            depth[nxt] = depth[state] + 1
            result.depth = max(result.depth, depth[nxt])
            bad = violated(nxt)
            if bad:
                return fail(nxt, bad)
            if max_states is not None and len(parent) >= max_states:
                result.truncated = True
                result.states = len(parent)
                return result
            frontier.append(nxt)

    result.states = len(parent)
    return result


def _trace(parent: Dict[State, Any], state: State) -> List[Step]:
    steps: List[Step] = []
    while parent[state] is not None:
        previous, action = parent[state]
        steps.append((action, state))
        state = previous
    steps.append(("Init", state))
    steps.reverse()
    return steps


def format_trace(model: Model, result: Result) -> str:
    """Render a counterexample trace, one numbered step per line."""
    lines = []
    for i, (action, state) in enumerate(result.trace):
        lines.append(f"  {i:2d}. {action:<34} {model.describe(state)}")
    return "\n".join(lines)
