"""Models for the tiny model checker (Chapter 5).

Each ``*_model()`` function returns a :class:`checker.Model`. States are
``NamedTuple`` values: immutable, hashable and readable in traces.

Run ``python3 models.py`` to check them all, or name some, for example
``python3 models.py naive-mutex lease-fencing``.

The bundled models:

* ``naive-mutex``      check-then-set lock: two processes both enter (FAILS)
* ``peterson``         Peterson's algorithm: mutual exclusion holds (PASSES)
* ``peterson-swapped`` Peterson with its two writes swapped (FAILS)
* ``lease-no-fencing`` lease lock, paused client writes late (FAILS)
* ``lease-fencing``    the same with fencing tokens (PASSES)
* ``two-phase-commit`` 2PC atomicity with 3 participants (PASSES)
* ``two-phase-commit-majority``  coordinator commits on a majority (FAILS)
"""

import sys
from typing import NamedTuple, Tuple

from checker import Model, check, format_trace


def _set(t: tuple, i: int, value) -> tuple:
    """Return a copy of tuple ``t`` with position ``i`` replaced."""
    return t[:i] + (value,) + t[i + 1:]


# ---------------------------------------------------------------------------
# (a) Naive mutual exclusion: check the flag, then set it.
# ---------------------------------------------------------------------------

class MutexState(NamedTuple):
    pc: Tuple[str, ...]     # per process: idle -> check -> set -> crit -> idle
    locked: bool            # the shared flag


def naive_mutex_model(processes: int = 2) -> Model:
    """Each process reads ``locked``; if it is false, *later* sets it.

    The read and the write are separate steps, so another process can run
    between them. That gap is the race the checker finds.
    """

    def init():
        yield MutexState(pc=("idle",) * processes, locked=False)

    def next_states(s: MutexState):
        for i, pc in enumerate(s.pc):
            if pc == "idle":
                yield f"P{i}: wants lock", s._replace(pc=_set(s.pc, i, "check"))
            elif pc == "check" and not s.locked:
                yield f"P{i}: sees lock free", s._replace(pc=_set(s.pc, i, "set"))
            elif pc == "set":
                yield f"P{i}: sets lock", s._replace(pc=_set(s.pc, i, "crit"), locked=True)
            elif pc == "crit":
                yield f"P{i}: releases lock", s._replace(pc=_set(s.pc, i, "idle"), locked=False)

    def describe(s: MutexState) -> str:
        return f"pc={list(s.pc)} locked={s.locked}"

    return Model(
        name=f"naive-mutex({processes})",
        initial_states=init,
        next_states=next_states,
        invariants={"MutualExclusion": lambda s: s.pc.count("crit") <= 1},
        describe=describe,
    )


# ---------------------------------------------------------------------------
# (b) Peterson's algorithm for two processes.
# ---------------------------------------------------------------------------

class PetersonState(NamedTuple):
    pc: Tuple[str, str]     # idle -> step1 -> step2 -> wait -> crit -> idle
    flag: Tuple[bool, bool]  # flag[i]: process i wants to enter
    turn: int               # whose turn it is to wait


def peterson_model(swap_writes: bool = False) -> Model:
    """Peterson (1981): ``flag[i] = True; turn = j; await not flag[j] or turn == i``.

    Every assignment and the await test are separate atomic steps, as they
    would be on a machine with sequentially consistent memory. With
    ``swap_writes=True`` the process sets ``turn`` *before* ``flag``, a
    plausible-looking reordering that breaks mutual exclusion.
    """

    def init():
        yield PetersonState(pc=("idle", "idle"), flag=(False, False), turn=0)

    def set_flag(s, i):
        return s._replace(flag=_set(s.flag, i, True))

    def set_turn(s, i):
        return s._replace(turn=1 - i)

    first, second = (set_turn, set_flag) if swap_writes else (set_flag, set_turn)
    first_name, second_name = (("turn = other", "flag = true") if swap_writes
                               else ("flag = true", "turn = other"))

    def next_states(s: PetersonState):
        for i in (0, 1):
            j = 1 - i
            pc = s.pc[i]
            if pc == "idle":
                yield f"P{i}: {first_name}", first(s, i)._replace(pc=_set(s.pc, i, "step2"))
            elif pc == "step2":
                yield f"P{i}: {second_name}", second(s, i)._replace(pc=_set(s.pc, i, "wait"))
            elif pc == "wait" and (not s.flag[j] or s.turn == i):
                yield f"P{i}: enters", s._replace(pc=_set(s.pc, i, "crit"))
            elif pc == "crit":
                yield f"P{i}: exits, flag = false", s._replace(
                    pc=_set(s.pc, i, "idle"), flag=_set(s.flag, i, False))

    def describe(s: PetersonState) -> str:
        return f"pc={list(s.pc)} flag={list(s.flag)} turn={s.turn}"

    return Model(
        name="peterson-swapped" if swap_writes else "peterson",
        initial_states=init,
        next_states=next_states,
        invariants={"MutualExclusion": lambda s: s.pc.count("crit") <= 1},
        describe=describe,
    )


# ---------------------------------------------------------------------------
# (c) A distributed lock with leases, with and without fencing tokens.
# ---------------------------------------------------------------------------

class LeaseClient(NamedTuple):
    pc: str                 # idle -> holding -> ready -> done
    token: int              # fencing token issued with the lease (0 = none)
    lease_until: int        # when this client's lease expires


class LeaseState(NamedTuple):
    now: int                # global time; clients cannot see it except by checking
    lease_until: int        # lock server: the current lease expires at this time
    next_token: int         # lock server: next fencing token to hand out
    clients: Tuple[LeaseClient, ...]
    max_token_seen: int     # storage: highest token accepted so far (fencing)
    writes: Tuple[int, ...]  # storage: tokens of the writes it accepted, in order


def lease_lock_model(fencing: bool, clients: int = 2, lease: int = 2,
                     max_time: int = 3) -> Model:
    """Kleppmann's stale-lease scenario (*Designing Data-Intensive Applications*, ch. 8).

    A lock server grants a lease of ``lease`` time units with a fencing
    token that increases on every grant. A client checks its lease is still
    valid and then writes to storage. Between the check and the write the
    client may *pause* (a garbage-collection stop, a swapped-out VM): the
    model expresses that simply by letting time tick and other clients run
    in between.

    Safety property: storage applies writes in lease order, so a write from
    an older lease never lands after a write from a newer one. Without
    fencing, storage accepts everything. With fencing, storage rejects a
    write whose token is lower than one it has already accepted.
    """

    def init():
        yield LeaseState(now=0, lease_until=0, next_token=1,
                         clients=(LeaseClient("idle", 0, 0),) * clients,
                         max_token_seen=0, writes=())

    def next_states(s: LeaseState):
        if s.now < max_time:
            yield "Clock ticks", s._replace(now=s.now + 1)
        for i, c in enumerate(s.clients):
            if c.pc == "idle" and s.now >= s.lease_until:
                granted = LeaseClient("holding", s.next_token, s.now + lease)
                yield (f"C{i}: acquires lease (token {s.next_token})",
                       s._replace(lease_until=s.now + lease, next_token=s.next_token + 1,
                                  clients=_set(s.clients, i, granted)))
            elif c.pc == "holding":
                if s.now < c.lease_until:
                    yield (f"C{i}: checks lease: valid",
                           s._replace(clients=_set(s.clients, i, c._replace(pc="ready"))))
                else:
                    yield (f"C{i}: checks lease: expired, gives up",
                           s._replace(clients=_set(s.clients, i, c._replace(pc="done"))))
            elif c.pc == "ready":
                done = _set(s.clients, i, c._replace(pc="done"))
                if fencing and c.token < s.max_token_seen:
                    yield f"C{i}: write (token {c.token}) REJECTED", s._replace(clients=done)
                else:
                    yield (f"C{i}: write (token {c.token}) accepted",
                           s._replace(clients=done, writes=s.writes + (c.token,),
                                      max_token_seen=max(s.max_token_seen, c.token)))

    def in_lease_order(s: LeaseState) -> bool:
        return all(a <= b for a, b in zip(s.writes, s.writes[1:]))

    def describe(s: LeaseState) -> str:
        cs = " ".join(f"C{i}={c.pc}/t{c.token}" for i, c in enumerate(s.clients))
        return f"now={s.now} lease_until={s.lease_until} {cs} writes={list(s.writes)}"

    return Model(
        name="lease-fencing" if fencing else "lease-no-fencing",
        initial_states=init,
        next_states=next_states,
        invariants={"WritesInLeaseOrder": in_lease_order},
        describe=describe,
    )


# ---------------------------------------------------------------------------
# (d) Two-phase commit.
# ---------------------------------------------------------------------------

class TwoPCState(NamedTuple):
    rm: Tuple[str, ...]     # participants: working | prepared | committed | aborted
    tm: str                 # coordinator: init | committed | aborted


def two_phase_commit_model(participants: int = 3, commit_on_majority: bool = False) -> Model:
    """Two-phase commit in the style of Lamport's TLA+ ``TwoPhase`` spec.

    Participants (resource managers, RMs) vote yes by becoming *prepared*,
    or vote no by aborting on their own. The coordinator (transaction
    manager, TM) commits only when every participant is prepared, and may
    abort at any time before that (for example on a timeout). Participants
    then learn the decision. Messages are abstracted away: the coordinator
    reads votes directly, which is enough to check the decision logic.

    ``commit_on_majority=True`` is a deliberate bug: the coordinator commits
    once a majority has voted yes.
    """

    def init():
        yield TwoPCState(rm=("working",) * participants, tm="init")

    def next_states(s: TwoPCState):
        for i, r in enumerate(s.rm):
            if r == "working":
                yield f"RM{i}: votes yes (prepared)", s._replace(rm=_set(s.rm, i, "prepared"))
                yield f"RM{i}: votes no (aborts)", s._replace(rm=_set(s.rm, i, "aborted"))
            if r == "prepared" and s.tm == "committed":
                yield f"RM{i}: learns commit", s._replace(rm=_set(s.rm, i, "committed"))
            if r in ("working", "prepared") and s.tm == "aborted":
                yield f"RM{i}: learns abort", s._replace(rm=_set(s.rm, i, "aborted"))
        if s.tm == "init":
            yes = s.rm.count("prepared")
            if yes == participants or (commit_on_majority and yes > participants // 2):
                yield "TM: decides commit", s._replace(tm="committed")
            yield "TM: decides abort", s._replace(tm="aborted")

    def atomic(s: TwoPCState) -> bool:
        return not ("committed" in s.rm and "aborted" in s.rm)

    def describe(s: TwoPCState) -> str:
        return f"TM={s.tm:<9} RMs={list(s.rm)}"

    return Model(
        name="two-phase-commit-majority" if commit_on_majority else "two-phase-commit",
        initial_states=init,
        next_states=next_states,
        invariants={"Atomicity": atomic},
        describe=describe,
    )


MODELS = {
    "naive-mutex": naive_mutex_model,
    "peterson": peterson_model,
    "peterson-swapped": lambda: peterson_model(swap_writes=True),
    "lease-no-fencing": lambda: lease_lock_model(fencing=False),
    "lease-fencing": lambda: lease_lock_model(fencing=True),
    "two-phase-commit": two_phase_commit_model,
    "two-phase-commit-majority": lambda: two_phase_commit_model(commit_on_majority=True),
}


def main(argv) -> int:
    names = argv or list(MODELS)
    unknown = [n for n in names if n not in MODELS]
    if unknown:
        print(f"unknown model(s): {', '.join(unknown)}; choose from {', '.join(MODELS)}")
        return 2
    for name in names:
        model = MODELS[name]()
        result = check(model)
        print(result.summary())
        if not result.ok:
            print(f"  shortest counterexample ({len(result.trace) - 1} steps):")
            print(format_trace(model, result))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
