"""Figure 8 of the Raft paper, replayed step by step.

Why may a leader not commit an entry from an earlier term just because it
is stored on a majority? Ongaro and Ousterhout's Figure 8 shows a schedule
in which such an entry is later overwritten. This script drives the real
``RaftNode`` code through that schedule by hand: a *manual network* holds
every message until the script decides to deliver or drop it, and timers
never fire unless the script fires them.

    (a) S1 leads term 2 and replicates entry 2 (term 2) to S2 only.
    (b) S1 crashes. S5 wins term 3 with votes from S3, S4 and itself and
        appends a different entry 2 (term 3), which no one else receives.
    (c) S5 crashes. S1 restarts, wins term 4 (S1, S2, S3), and copies its
        entry 2 (term 2) to S3. That entry is now on a majority (S1, S2, S3).
        S1 also appends entry 3 (term 4), so far only on S1.
        A buggy leader commits entry 2 here, by counting replicas.
    (d) S1 crashes. S5 restarts and wins term 5 with votes from S2, S3 and
        S4: its last log term (3) beats theirs (2 or 1). It replicates its
        entry 2 (term 3) everywhere, overwriting the "committed" entry.

With the Figure 8 rule, S1 in (c) does not commit entry 2, so nothing is
lost in (d). With ``bugs={"commit_previous_term"}`` the invariant checker
reports Leader Completeness and State Machine Safety violations.

Run ``python3 figure8.py``.
"""

import random
from typing import Callable, Dict, List

from invariants import InvariantChecker
from raft import (AppendEntries, ClientRequest, Command, RaftConfig, RaftNode,
                  RequestVote)

IDS = ["S1", "S2", "S3", "S4", "S5"]


class ManualScheduler:
    """Timers are ignored: the script decides when elections happen."""

    now = 0.0

    def after(self, delay, fn, *args) -> None:
        pass


class ManualNetwork:
    """Holds messages in flight until the script delivers or drops them."""

    def __init__(self) -> None:
        self.in_flight: List[tuple] = []
        self.nodes: Dict[str, RaftNode] = {}

    def send(self, src: str, dst: str, msg) -> None:
        self.in_flight.append((src, dst, msg))

    def deliver(self, match: Callable[[str, str, object], bool]) -> int:
        """Deliver every in-flight message that matches; drop nothing else."""
        ready = [m for m in self.in_flight if match(*m)]
        self.in_flight = [m for m in self.in_flight if not match(*m)]
        for src, dst, msg in ready:
            if dst in self.nodes:
                self.nodes[dst].receive(src, msg)
        return len(ready)

    def drop_all(self) -> None:
        self.in_flight.clear()


class Figure8:
    def __init__(self, bugs=frozenset()) -> None:
        self.network = ManualNetwork()
        scheduler = ManualScheduler()
        rng = random.Random(0)
        self.nodes = {i: RaftNode(i, IDS, scheduler, self.network, rng, RaftConfig(), bugs)
                      for i in IDS}
        self.network.nodes = self.nodes
        self.checker = InvariantChecker(self.nodes, stop_on_violation=False)
        self.lines: List[str] = []
        self.seq = 0
        self._shown = 0

    def check(self) -> None:
        self.checker.check()

    def show(self, caption: str) -> None:
        self.lines.append(caption)
        for n in self.nodes.values():
            self.lines.append("    " + n.describe())
        new = self.checker.violations[self._shown:]
        self._shown = len(self.checker.violations)
        kinds: Dict[str, list] = {}
        for v in new:
            kinds.setdefault(v.invariant, []).append(v)
        for name, vs in kinds.items():
            more = f" (+{len(vs) - 1} more like it)" if len(vs) > 1 else ""
            self.lines.append(f"    !! {name}: {vs[0].detail}{more}")

    # -- script steps -------------------------------------------------------
    def elect(self, candidate: str, voters: List[str]) -> bool:
        """``candidate`` times out; only ``voters`` hear its RequestVote."""
        node = self.nodes[candidate]
        node.on_election_timeout()
        self.network.deliver(lambda s, d, m: s == candidate and isinstance(m, RequestVote)
                             and d in voters)
        self.network.deliver(lambda s, d, m: d == candidate)       # the replies
        self.network.drop_all()           # other requests and first heartbeats are lost
        self.check()
        return node.role == "leader"

    def client_put(self, leader: str, value: int) -> None:
        """A client command reaches the leader, which appends it locally."""
        self.seq += 1
        self.nodes[leader].receive("client", ClientRequest(Command("client", self.seq, "put", "x", value)))
        self.network.drop_all()           # its AppendEntries are lost
        self.check()

    def replicate(self, leader: str, to: List[str]) -> None:
        """The leader sends AppendEntries to ``to``; those messages and replies get through."""
        node = self.nodes[leader]
        for _ in range(10):               # repeat until logs match (back-up on rejection)
            for peer in to:
                node.send_append(peer)
            self.network.deliver(lambda s, d, m: s == leader and d in to)
            self.network.deliver(lambda s, d, m: d == leader)
            self.network.drop_all()
            self.check()
            if all(node.match_index[p] >= node.last_index() for p in to):
                break

    def crash(self, node_id: str) -> None:
        self.nodes[node_id].crash()
        self.check()

    def restart(self, node_id: str) -> None:
        self.nodes[node_id].restart()
        self.check()

    # -- the scenario -------------------------------------------------------
    def run(self) -> "Figure8":
        assert self.elect("S2", IDS)                        # term 1: S2 leads
        self.client_put("S2", 1)
        self.replicate("S2", ["S1", "S3", "S4", "S5"])      # entry 1 committed everywhere
        self.replicate("S2", ["S1", "S3", "S4", "S5"])      # followers learn the commit
        self.show("start: entry 1 (term 1) committed on all servers")

        assert self.elect("S1", ["S2", "S3"])              # term 2
        self.client_put("S1", 2)
        self.replicate("S1", ["S2"])
        self.show("(a) S1 leads term 2; entry 2 (term 2) reaches S2 only")

        self.crash("S1")
        assert not self.elect("S5", ["S3", "S4"])          # term 2: S3 already voted for S1
        assert self.elect("S5", ["S3", "S4"])              # term 3
        self.client_put("S5", 3)
        self.show("(b) S1 crashes; S5 leads term 3 and appends entry 2 (term 3) locally")

        self.crash("S5")
        self.restart("S1")
        assert not self.elect("S1", ["S2", "S3", "S4"])    # term 3: S3, S4 already voted
        assert self.elect("S1", ["S2", "S3"])              # term 4
        self.replicate("S1", ["S2", "S3"])                 # S1 learns S2 and S3 hold entry 2
        self.client_put("S1", 4)
        self.show("(c) S5 crashes; S1 leads term 4, copies entry 2 (term 2) to S3, "
                  "appends entry 3 (term 4)")

        self.crash("S1")
        self.restart("S5")
        assert not self.elect("S5", ["S2", "S3", "S4"])    # term 4: S2, S3 already voted
        assert self.elect("S5", ["S2", "S3", "S4"])        # term 5
        self.client_put("S5", 5)
        self.replicate("S5", ["S2", "S3", "S4"])
        self.replicate("S5", ["S2", "S3", "S4"])
        self.show("(d) S1 crashes; S5 leads term 5 and overwrites entry 2 everywhere")
        return self


def main() -> None:
    for bugs, title in ((frozenset(), "Correct Raft (Figure 8 rule)"),
                        (frozenset({"commit_previous_term"}), "BUG: commit_previous_term")):
        print(f"===== {title}")
        f = Figure8(bugs).run()
        print("\n".join(f.lines))
        first, by = f.checker.applied[2]
        now = f.nodes["S5"].log[1]
        print(f"  index 2 was first applied by {by} as put x={first.command.value}; "
              f"the cluster's index 2 is now put x={now.command.value}. "
              f"Violations: {len(f.checker.violations)}\n")


if __name__ == "__main__":
    main()
