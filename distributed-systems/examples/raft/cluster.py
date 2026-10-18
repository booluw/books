"""A simulated five-node Raft cluster with a client and a fault injector.

``Cluster`` wires five :class:`raft.RaftNode` servers and a key-value
:class:`Client` to a simulated :class:`sim.Network`, and checks every
invariant in ``invariants.py`` after every single event.

A *nemesis* (Jepsen's word for the fault injector) can crash and restart
servers and split the network into partitions at random moments.

Run ``python3 cluster.py`` for a demonstration:

* a stable run: election time and committed commands;
* a chaotic run: partitions, crashes, loss, duplication, with all
  invariants holding;
* the same chaotic schedules with a deliberate bug switched on, until the
  checker catches it.
"""

import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from invariants import InvariantChecker, InvariantViolation
from raft import LEADER, ClientReply, ClientRequest, Command, RaftConfig, RaftNode
from sim import NetConfig, Network, Scheduler

NODE_IDS = ["S1", "S2", "S3", "S4", "S5"]


class Client:
    """Sends ``put`` commands one at a time, retrying until each is acknowledged.

    It keeps the same sequence number on every retry, so the state machine
    can recognise a command that was committed twice and apply it once.
    """

    def __init__(self, name: str, cluster: "Cluster", commands: int,
                 timeout: float = 400.0) -> None:
        self.name = name
        self.cluster = cluster
        self.rng = cluster.rng
        self.commands = commands
        self.timeout = timeout
        self.seq = 0
        self.target = cluster.rng.choice(NODE_IDS)
        self.completed: Dict[int, float] = {}      # seq -> time acknowledged
        self.retries = 0
        self._generation = 0

    def start(self) -> None:
        self._next()

    def _next(self) -> None:
        if self.seq >= self.commands:
            return
        self.seq += 1
        self._send()

    def _command(self) -> Command:
        return Command(self.name, self.seq, "put", f"k{self.seq % 3}", self.seq)

    def _send(self) -> None:
        self._generation += 1
        generation = self._generation
        self.cluster.network.send(self.name, self.target, ClientRequest(self._command()))

        def on_timeout():
            if generation == self._generation and self.seq not in self.completed:
                self.retries += 1
                self.target = self.rng.choice(NODE_IDS)
                self._send()
        self.cluster.scheduler.after(self.timeout, on_timeout)

    def receive(self, src: str, m: ClientReply) -> None:
        if m.seq != self.seq or self.seq in self.completed:
            return                                  # late or duplicate reply
        if m.ok:
            self.completed[m.seq] = self.cluster.scheduler.now
            self.cluster.scheduler.after(5.0, self._next)
        else:
            self.target = m.leader_hint or self.rng.choice(NODE_IDS)
            self.retries += 1
            self._generation += 1                   # cancel the pending timeout
            self.cluster.scheduler.after(10.0, self._send)


@dataclass
class NemesisConfig:
    interval: tuple = (100.0, 600.0)     # ms between faults
    crash: float = 0.3                   # relative weights of each fault
    restart: float = 0.3
    partition: float = 0.25
    heal: float = 0.15


class Cluster:
    def __init__(self, seed: int, net: Optional[NetConfig] = None,
                 config: Optional[RaftConfig] = None, bugs=frozenset(),
                 check: bool = True, stop_on_violation: bool = True) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.scheduler = Scheduler()
        self.network = Network(self.scheduler, self.rng, net)
        self.nodes: Dict[str, RaftNode] = {}
        for node_id in NODE_IDS:
            node = RaftNode(node_id, NODE_IDS, self.scheduler, self.network, self.rng,
                            config, frozenset(bugs))
            self.nodes[node_id] = node
            self.network.register(node_id, node.receive)
        self.checker = InvariantChecker(self.nodes, stop_on_violation) if check else None
        self.clients: List[Client] = []
        self.events: List[str] = []       # what the nemesis did, for reports
        self._nemesis_until = 0.0
        for node in self.nodes.values():
            node.start()

    # -- running -----------------------------------------------------------
    def add_client(self, commands: int, name: str = "client") -> Client:
        client = Client(name, self, commands)
        self.network.register(name, client.receive, server=False)
        self.clients.append(client)
        self.scheduler.after(1.0, client.start)
        return client

    def run(self, until: float) -> None:
        """Process events up to virtual time ``until``, checking invariants
        after each one. Raises InvariantViolation on the first failure."""
        while True:
            t = self.scheduler.next_time()
            if t is None or t > until:
                break
            self.scheduler.step()
            if self.checker:
                self.checker.check(self.scheduler.now)
        self.scheduler.now = max(self.scheduler.now, until)

    def run_until(self, condition, limit: float, poll: float = 1.0) -> Optional[float]:
        """Run until ``condition()`` holds; return the time, or None at ``limit``."""
        while self.scheduler.now < limit:
            if condition():
                return self.scheduler.now
            self.run(self.scheduler.now + poll)
        return self.scheduler.now if condition() else None

    # -- observing ----------------------------------------------------------
    def leaders(self) -> List[RaftNode]:
        return [n for n in self.nodes.values() if n.alive and n.role == LEADER]

    def leader(self) -> Optional[RaftNode]:
        """The leader of the highest term, if a live one exists."""
        leaders = self.leaders()
        return max(leaders, key=lambda n: n.current_term) if leaders else None

    def describe(self) -> str:
        return "\n".join("  " + n.describe() for n in self.nodes.values())

    # -- faults ------------------------------------------------------------
    def crash(self, node_id: str) -> None:
        self.nodes[node_id].crash()
        self.events.append(f"t={self.scheduler.now:.0f} crash {node_id}")

    def restart(self, node_id: str) -> None:
        self.nodes[node_id].restart()
        self.events.append(f"t={self.scheduler.now:.0f} restart {node_id}")

    def partition(self, *groups) -> None:
        self.network.partition(groups)
        self.events.append(f"t={self.scheduler.now:.0f} partition {[sorted(g) for g in groups]}")

    def heal(self) -> None:
        self.network.heal()
        self.events.append(f"t={self.scheduler.now:.0f} heal")

    def start_nemesis(self, until: float, config: Optional[NemesisConfig] = None) -> None:
        """Inject random faults until virtual time ``until``."""
        cfg = config or NemesisConfig()
        self._nemesis_until = until

        def act():
            if self.scheduler.now >= self._nemesis_until:
                return
            kinds = ["crash", "restart", "partition", "heal"]
            kind = self.rng.choices(kinds, [cfg.crash, cfg.restart, cfg.partition, cfg.heal])[0]
            up = [n for n, node in self.nodes.items() if node.alive]
            down = [n for n, node in self.nodes.items() if not node.alive]
            if kind == "crash" and up:
                self.crash(self.rng.choice(up))
            elif kind == "restart" and down:
                self.restart(self.rng.choice(down))
            elif kind == "partition":
                shuffled = self.rng.sample(NODE_IDS, len(NODE_IDS))
                cut = self.rng.randint(1, len(NODE_IDS) - 1)
                self.partition(shuffled[:cut], shuffled[cut:])
            elif kind == "heal":
                self.heal()
            self.scheduler.after(self.rng.uniform(*cfg.interval), act)

        self.scheduler.after(self.rng.uniform(*cfg.interval), act)

    def stop_faults(self) -> None:
        """Heal the network and restart every crashed server."""
        self._nemesis_until = self.scheduler.now
        self.heal()
        for node_id, node in self.nodes.items():
            if not node.alive:
                self.restart(node_id)


# ---------------------------------------------------------------------------
# Ready-made experiments
# ---------------------------------------------------------------------------

CHAOS_NET = NetConfig(delay=(2.0, 30.0), loss=0.05, duplicate=0.05)


@dataclass
class ChaosResult:
    seed: int
    violation: Optional[str] = None
    steps: int = 0
    committed: int = 0
    terms: int = 0
    faults: List[str] = field(default_factory=list)


def chaos_run(seed: int, bugs=frozenset(), duration: float = 5000.0,
              commands: int = 60) -> ChaosResult:
    """One randomised schedule: lossy network, partitions, crashes, restarts."""
    cluster = Cluster(seed, net=CHAOS_NET, bugs=bugs)
    cluster.add_client(commands)
    cluster.start_nemesis(until=duration)
    result = ChaosResult(seed)
    try:
        cluster.run(duration)
    except InvariantViolation as e:
        result.violation = str(e.violation)
    result.steps = cluster.scheduler.steps
    result.committed = len(cluster.checker.committed)
    result.terms = max(n.current_term for n in cluster.nodes.values())
    result.faults = cluster.events
    return result


def find_bug(bug: str, seeds, **kw) -> Optional[ChaosResult]:
    """Return the first chaos run in which the invariant checker catches ``bug``."""
    for seed in seeds:
        result = chaos_run(seed, bugs={bug}, **kw)
        if result.violation:
            return result
    return None


def main(argv) -> None:
    runs = int(argv[0]) if argv else 100
    print("== Stable network, seed 1")
    cluster = Cluster(1)
    client = cluster.add_client(20)
    elected = cluster.run_until(lambda: cluster.leader() is not None, limit=2000)
    print(f"  leader {cluster.leader().id} elected at t={elected:.0f}ms "
          f"in term {cluster.leader().current_term}")
    done = cluster.run_until(lambda: len(client.completed) == 20, limit=5000)
    print(f"  20 commands committed and acknowledged by t={done:.0f}ms; "
          f"{cluster.checker.checks} invariant checks passed")
    print(cluster.describe())

    print(f"\n== {runs} chaotic schedules (5% loss, 5% duplication, partitions, crashes)")
    totals = {"steps": 0, "committed": 0, "violations": 0}
    for seed in range(runs):
        r = chaos_run(seed)
        totals["steps"] += r.steps
        totals["committed"] += r.committed
        totals["violations"] += bool(r.violation)
    print(f"  {totals['steps']} events checked, {totals['committed']} entries committed, "
          f"{totals['violations']} invariant violations")

    for bug in ("vote_without_log_check", "commit_previous_term"):
        print(f"\n== Bug {bug!r}: searching chaotic schedules from seed 0")
        found = find_bug(bug, range(500))
        if found:
            print(f"  caught on seed {found.seed}: {found.violation}")
            print("  faults before it: " + "; ".join(found.faults[-6:]))
        else:
            print("  not caught in 500 seeds (see figure8.py for a scripted trace)")


if __name__ == "__main__":
    main(sys.argv[1:])
