"""Linearizability and sequential consistency checking (Chapters 8 and 23).

A history is **linearizable** if we can pick one instant (a *linearization
point*) inside each operation's interval, between invocation and return,
so that taking the operations in the order of those instants gives results
a single, sequential register would have given. Equivalently: there is a
total order of the operations that

1. respects real time: if A returned before B was invoked, A comes first;
2. is legal for the sequential specification (every read returns the
   latest write before it in the order).

A history is **sequentially consistent** if there is a legal total order
that respects only each client's own *program order*, not real time
across clients. Every linearizable history is sequentially consistent;
the converse fails, and ``histories.py`` has examples.

The search is the Wing & Gong algorithm (1993): repeatedly pick an
operation that may come next, apply it to the model, and backtrack when a
result is impossible. On its own that is exponential. Lowe (2017) added the
memoisation that tools such as Knossos and Porcupine rely on: the future of
the search depends only on *which* operations have been linearized and the
*state* of the register, not on the order chosen so far, so each
``(set of linearized operations, state)`` pair needs exploring only once.
"""

import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List, Optional, Set, Tuple

from history import Op, step, validate


@dataclass
class Result:
    ok: bool
    order: Optional[List[Op]]
    """A witness: a legal total order containing every completed operation
    (and any pending ones that must have taken effect). ``None`` if not ok."""
    explored: int
    """Search nodes visited; a rough measure of the work done."""
    longest_prefix: List[Op] = field(default_factory=list)
    """On failure, the longest legal ordering found before getting stuck.
    The operation that cannot be added after it is usually the culprit."""


def _search(ops: List[Op], init: Any,
            can_go_next: Callable[[int, int, float], bool], memo: bool = True) -> Result:
    """Depth-first search for a legal total order.

    ``can_go_next(i, done, min_ret)`` says whether operation ``i`` may be
    placed next, given the set of already-placed operations as a bitmask
    ``done`` and the earliest return time among the unplaced operations.
    """
    n = len(ops)
    required = 0
    for i, op in enumerate(ops):
        if not op.pending:
            required |= 1 << i
    seen: Set[Tuple[int, Any]] = set()
    best: List[int] = []
    explored = 0

    def dfs(done: int, state: Any, order: List[int]) -> bool:
        nonlocal explored, best
        explored += 1
        if done & required == required:
            return True          # every completed op placed; pending ones are optional
        if memo:
            if (done, state) in seen:
                return False     # explored before, from a different order: dead end
            seen.add((done, state))
        if len(order) > len(best):
            best = list(order)
        min_ret = min(ops[j].ret for j in range(n) if not done >> j & 1)
        for i in range(n):
            if done >> i & 1 or not can_go_next(i, done, min_ret):
                continue
            legal, new_state = step(state, ops[i])
            if not legal:
                continue
            order.append(i)
            if dfs(done | 1 << i, new_state, order):
                return True
            order.pop()
        return False

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 4 * n + 1000))
    try:
        order: List[int] = []
        found = dfs(0, init, order)
    finally:
        sys.setrecursionlimit(old_limit)
    if found:
        return Result(True, [ops[i] for i in order], explored)
    return Result(False, None, explored, [ops[i] for i in best])


def check_linearizable(history: Iterable[Op], init: Any = 0, memo: bool = True) -> Result:
    """Is the history linearizable for a register starting at ``init``?

    ``memo=False`` turns off Lowe's memoisation, giving plain Wing & Gong,
    so you can watch the search blow up on concurrent histories.

    Operation ``i`` may go next only if no other unplaced operation returned
    before ``i`` was invoked (otherwise that one must come first). Since
    ``i`` itself returns after it is invoked, that is the same as: ``i`` was
    invoked no later than the earliest return among unplaced operations.
    """
    ops = sorted(validate(history), key=lambda o: o.call)

    def can_go_next(i: int, done: int, min_ret: float) -> bool:
        return ops[i].call <= min_ret

    return _search(ops, init, can_go_next, memo)


def check_sequentially_consistent(history: Iterable[Op], init: Any = 0) -> Result:
    """Is there a legal order that respects each client's program order?

    Operation ``i`` may go next only if it is the earliest unplaced
    operation of its own client. Real time across clients is ignored.
    """
    ops = sorted(validate(history), key=lambda o: o.call)
    earlier_same_client = [
        [j for j in range(len(ops)) if ops[j].client == op.client and ops[j].call < op.call]
        for op in ops
    ]

    def can_go_next(i: int, done: int, min_ret: float) -> bool:
        return all(done >> j & 1 for j in earlier_same_client[i])

    return _search(ops, init, can_go_next)


def brute_force_linearizable(history: Iterable[Op], init: Any = 0) -> bool:
    """Reference implementation for tests: try every permutation.

    Only usable for tiny histories (8 operations is 40,320 orders).
    Pending operations may be included or left out.
    """
    from itertools import combinations, permutations

    ops = validate(history)
    completed = [o for o in ops if not o.pending]
    pending = [o for o in ops if o.pending]
    for k in range(len(pending) + 1):
        for chosen in combinations(pending, k):
            for perm in permutations(completed + list(chosen)):
                if any(perm[b].ret < perm[a].call
                       for a in range(len(perm)) for b in range(a + 1, len(perm))):
                    continue
                state, legal = init, True
                for op in perm:
                    legal, state = step(state, op)
                    if not legal:
                        break
                if legal:
                    return True
    return False
