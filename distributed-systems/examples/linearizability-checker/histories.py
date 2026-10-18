"""Textbook register histories, with the verdicts they should get.

Run ``python3 histories.py`` to check each one and draw it as a timeline.
All registers start at 0. Clients are A, B and C; times are abstract units.
"""

import textwrap
from typing import Dict, List, NamedTuple

from checker import check_linearizable, check_sequentially_consistent
from history import Op, cas, read, render, write


class Example(NamedTuple):
    ops: List[Op]
    linearizable: bool
    sequentially_consistent: bool
    note: str


EXAMPLES: Dict[str, Example] = {
    "read-after-write": Example(
        [write("A", 1, 0, 1), read("B", 1, 2, 3)],
        True, True,
        "The write finished before the read began, and the read sees it."),

    "stale-read": Example(
        [write("A", 1, 0, 1), read("B", 0, 2, 3)],
        False, True,
        "The read began after the write finished but returned the old value. "
        "Sequential consistency allows it (order the read first: different "
        "clients); linearizability does not. This is a follower serving a "
        "read before replication caught up."),

    "concurrent-read-either-value": Example(
        [write("A", 1, 0, 10), read("B", 0, 1, 2), read("C", 1, 3, 4)],
        True, True,
        "Reads that overlap a write may return the old or the new value, "
        "as long as they never go backwards."),

    "new-old-inversion": Example(
        [write("A", 1, 0, 10), read("B", 1, 1, 2), read("C", 0, 3, 4)],
        False, True,
        "Both reads overlap the write, but once B has seen 1, a read that "
        "starts later must not see 0. Each read is defensible alone; the pair "
        "is not linearizable."),

    "read-from-the-future": Example(
        [read("A", 1, 0, 1), write("B", 1, 2, 3)],
        False, True,
        "A read returned a value before anyone had started writing it. "
        "Sequential consistency happily reorders across clients."),

    "own-write-lost": Example(
        [write("A", 1, 0, 1), read("A", 0, 2, 3)],
        False, False,
        "A client cannot see its own write. Not even sequentially "
        "consistent: program order puts the write first."),

    "writes-seen-in-different-orders": Example(
        [write("A", 1, 0, 1), write("A", 2, 2, 3),
         read("B", 2, 4, 5), read("B", 1, 6, 7)],
        False, False,
        "B sees 2 then 1, but A wrote 1 then 2. No single order explains "
        "it, whatever the timing."),

    "two-cas-both-succeed": Example(
        [cas("A", 0, 1, True, 0, 5), cas("B", 0, 2, True, 1, 6)],
        False, False,
        "Two compare-and-set operations from 0 cannot both succeed: "
        "whichever goes second sees the other's value."),

    "two-cas-one-fails": Example(
        [cas("A", 0, 1, True, 0, 5), cas("B", 0, 2, False, 1, 6), read("C", 1, 7, 8)],
        True, True,
        "One CAS wins, the other fails, and a later read sees the winner."),

    "pending-write-may-be-ignored": Example(
        [write("A", 1, 0), read("B", 0, 5, 6)],
        True, True,
        "A's write never returned (A crashed). It may never have happened, "
        "so reading 0 is fine."),

    "pending-write-must-have-happened": Example(
        [write("A", 1, 0), read("B", 1, 5, 6), read("C", 0, 7, 8)],
        False, True,
        "B saw the pending write, so it took effect before B returned; C, "
        "starting later, cannot see 0."),
}


def main() -> None:
    for name, ex in EXAMPLES.items():
        lin = check_linearizable(ex.ops)
        sc = check_sequentially_consistent(ex.ops)
        print(f"== {name}: linearizable={lin.ok} sequentially consistent={sc.ok}")
        print(render(ex.ops, width=40, order=lin.order if lin.ok else None))
        if lin.ok:
            print("   witness: " + ", ".join(o.label() for o in lin.order))
        elif sc.ok:
            print("   sequential witness (ignores real time): "
                  + ", ".join(o.label() for o in sc.order))
        else:
            print("   longest legal prefix: "
                  + (", ".join(o.label() for o in lin.longest_prefix) or "(none)"))
        print(textwrap.fill(ex.note, width=78, initial_indent="   ",
                            subsequent_indent="   ") + "\n")


if __name__ == "__main__":
    main()
