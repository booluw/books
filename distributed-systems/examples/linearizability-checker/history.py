"""Operations, histories and the register model (Chapters 8 and 23).

A *history* is what a test harness records while clients talk to a
storage system: for every operation, which client issued it, what it was,
what came back, when it was *invoked* (the call left the client) and when
it *returned* (the response arrived). We never see when the operation took
effect inside the system; we only know it was somewhere between the two.

This module defines the operation record, a few constructors that read
well in tests, the sequential specification of a single register, and a
small text renderer that draws a history as a timeline.
"""

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Tuple

PENDING = float("inf")
"""Return time of an operation that never returned (the client crashed or
timed out). It may or may not have taken effect."""


@dataclass(frozen=True)
class Op:
    """One operation on the register.

    ``kind`` is ``"read"``, ``"write"`` or ``"cas"``:

    * write: ``arg`` is the value written; ``result`` is ``None``.
    * read: ``arg`` is ``None``; ``result`` is the value returned.
    * cas (compare-and-set): ``arg`` is ``(expected, new)``; ``result`` is
      ``True`` if the register held ``expected`` and now holds ``new``,
      ``False`` if it held something else and was left unchanged.
    """

    client: str
    kind: str
    arg: Any
    result: Any
    call: float
    ret: float = PENDING

    @property
    def pending(self) -> bool:
        return self.ret == PENDING

    def label(self) -> str:
        if self.kind == "write":
            text = f"W({self.arg})"
        elif self.kind == "read":
            text = f"R()->{'?' if self.pending else self.result}"
        else:
            expected, new = self.arg
            outcome = "?" if self.pending else ("ok" if self.result else "fail")
            text = f"CAS({expected}->{new}):{outcome}"
        return f"{self.client}:{text}"

    def __str__(self) -> str:
        end = "pending" if self.pending else f"{self.ret:g}"
        return f"{self.label()} [{self.call:g}, {end}]"


def write(client: str, value: Any, call: float, ret: float = PENDING) -> Op:
    return Op(client, "write", value, None, call, ret)


def read(client: str, value: Any, call: float, ret: float = PENDING) -> Op:
    return Op(client, "read", None, value, call, ret)


def cas(client: str, expected: Any, new: Any, ok: bool, call: float,
        ret: float = PENDING) -> Op:
    return Op(client, "cas", (expected, new), ok, call, ret)


def step(state: Any, op: Op) -> Tuple[bool, Any]:
    """The register's *sequential specification*.

    Applies ``op`` to a register holding ``state`` as if nothing else were
    happening. Returns ``(legal, new_state)``: ``legal`` is False when the
    recorded result could not have come from this state. A pending
    operation's result is unknown, so any result is legal for it.
    """
    if op.kind == "write":
        return True, op.arg
    if op.kind == "read":
        return op.pending or op.result == state, state
    if op.kind == "cas":
        expected, new = op.arg
        if state == expected:
            return op.pending or op.result is True, new
        return op.pending or op.result is False, state
    raise ValueError(f"unknown operation kind {op.kind!r}")


def validate(history: Iterable[Op]) -> List[Op]:
    """Check the history is *well formed* and return it as a list.

    Each operation must return after it is invoked, and each client must be
    sequential: it invokes its next operation only after the previous one
    returned (so a pending operation is always the client's last). Program
    order, which sequential consistency relies on, is only defined then.
    """
    ops = list(history)
    last: dict = {}
    for op in sorted(ops, key=lambda o: o.call):
        if op.ret < op.call:
            raise ValueError(f"{op}: returns before it is invoked")
        previous = last.get(op.client)
        if previous is not None and previous.ret >= op.call:
            raise ValueError(f"{op}: client {op.client} still waiting for {previous}")
        last[op.client] = op
    return ops


def render(history: Iterable[Op], width: int = 60, order: Optional[List[Op]] = None) -> str:
    """Draw each operation as a bar on a shared time axis.

    If ``order`` (a linearization) is given, each line is prefixed with the
    operation's position in it, or ``-`` if it is not included.
    """
    ops = sorted(history, key=lambda o: (o.call, o.client))
    if not ops:
        return "(empty history)"
    finite = [o.ret for o in ops if not o.pending] + [o.call for o in ops]
    start, end = min(finite), max(finite)
    span = (end - start) or 1.0
    scale = (width - 1) / span

    def col(t: float) -> int:
        return width - 1 if t == PENDING else int(round((t - start) * scale))

    position = {id(op): i for i, op in enumerate(order)} if order else {}
    lines = []
    for op in ops:
        a, b = col(op.call), col(op.ret)
        bar = [" "] * width
        for x in range(a, b + 1):
            bar[x] = "-"
        bar[a] = "|"
        bar[b] = ">" if op.pending else "|"
        prefix = ""
        if order is not None:
            prefix = f"{position[id(op)] + 1:>3} " if id(op) in position else "  - "
        lines.append(f"{prefix}{op.label():<22} {''.join(bar)}")
    return "\n".join(lines)
