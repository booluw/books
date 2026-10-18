"""The system under test: a primary-backup replicated set of counters.

Clients send ``incr(counter, op_id)`` to the primary. The primary applies the
increment, replicates it to the backup, waits for the backup's
acknowledgement and only then tells the client "ok". If the primary
crashes, a failure detector promotes the backup. The promise to clients:

    **No acknowledged write is lost**: every op a client was told "ok" for
    is in the final state of whichever node is primary at the end.

Each counter's state is the *set* of op ids applied to it (its value is the
size of the set), so retries are idempotent: applying op 17 twice still
counts once.

The deliberate bug
------------------
``BuggyPrimary`` matches backup acknowledgements by **counter name** rather
than by **op id**. When two clients increment the same counter at about the
same time, the ack for the first op also releases the second, so the client
is told "ok" before the backup has the second op. That is harmless unless
the replication message for the second op is *also* dropped (the primary
stops retransmitting, because it thinks the op is done) *and* the primary
later crashes, so the backup takes over without it. Three unlikely things
in one run: exactly the kind of bug that passes unit tests and code review,
and turns up in production months later.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sim import Simulator, SwarmConfig


class Node:
    def __init__(self, sim: Simulator, name: str, cluster: "Cluster"):
        self.sim, self.name, self.cluster = sim, name, cluster
        self.alive = True
        self.state: dict[str, set[int]] = {}
        self.pending: dict[int, tuple[str, str]] = {}   # op id -> (client, counter)
        self.is_primary = False

    def apply(self, counter: str, op: int) -> None:
        self.state.setdefault(counter, set()).add(op)

    def has(self, counter: str, op: int) -> bool:
        return op in self.state.get(counter, set())

    # ---- message handling ---------------------------------------------------
    def receive(self, src: str, msg: tuple) -> None:
        kind = msg[0]
        if kind == "incr" and self.is_primary:
            _, op, counter, client = msg
            self.on_incr(op, counter, client)
        elif kind == "replicate":
            _, op, counter = msg
            self.apply(counter, op)
            self.sim.send(self.name, src, ("ack", op, counter))
        elif kind == "ack" and self.is_primary:
            _, op, counter = msg
            self.on_ack(op, counter)

    def on_incr(self, op: int, counter: str, client: str) -> None:
        if self.has(counter, op) and op not in self.pending:
            self.sim.send(self.name, client, ("ok", op))     # a retry of a finished op
            return
        self.apply(counter, op)
        if self.cluster.backup_alive():
            self.pending[op] = (client, counter)
            self.replicate(op)
        else:                                                 # running alone after failover
            self.sim.send(self.name, client, ("ok", op))

    def replicate(self, op: int) -> None:
        if not (self.alive and self.is_primary and op in self.pending):
            return
        if not self.cluster.backup_alive():                   # backup died: finish alone
            client, _ = self.pending.pop(op)
            self.sim.send(self.name, client, ("ok", op))
            return
        _, counter = self.pending[op]
        self.sim.send(self.name, self.cluster.backup_name(), ("replicate", op, counter))
        self.sim.schedule(self.sim.config.retransmit, self.replicate, op)

    def on_ack(self, op: int, counter: str) -> None:
        """Correct: release exactly the op the backup acknowledged."""
        if op in self.pending:
            client, _ = self.pending.pop(op)
            self.sim.send(self.name, client, ("ok", op))


class BuggyNode(Node):
    def on_ack(self, op: int, counter: str) -> None:
        """BUG: releases every pending op on the same counter, including ops
        the backup has not received yet."""
        released = [other for other, (_, c) in self.pending.items() if c == counter]
        if released:
            self.sim.log(f"{self.name} ack for op {op} on {counter} releases ops {released}")
        for other in released:
            client, _ = self.pending.pop(other)
            self.sim.send(self.name, client, ("ok", other))


class Client:
    def __init__(self, sim: Simulator, name: str, cluster: "Cluster", ops: list[tuple[int, str]]):
        self.sim, self.name, self.cluster = sim, name, cluster
        self.todo = list(ops)
        self.current: tuple[int, str] | None = None
        self.acked: list[tuple[int, str]] = []

    def start(self) -> None:
        self.sim.schedule(self.sim.rng.uniform(0, 20), self.next_op)

    def next_op(self) -> None:
        if not self.todo:
            return
        self.current = self.todo.pop(0)
        self.send_current()

    def send_current(self) -> None:
        op, counter = self.current
        self.sim.send(self.name, self.cluster.primary_name(), ("incr", op, counter, self.name))
        self.sim.schedule(self.sim.config.client_timeout, self.on_timeout, op)

    def on_timeout(self, op: int) -> None:
        if self.current and self.current[0] == op:
            self.sim.log(f"{self.name} timeout op{op}, retrying")
            self.send_current()

    def receive(self, src: str, msg: tuple) -> None:
        if msg[0] == "ok" and self.current and msg[1] == self.current[0]:
            self.acked.append(self.current)
            self.current = None
            self.sim.schedule(self.sim.rng.uniform(0, 5), self.next_op)


@dataclass
class Cluster:
    sim: Simulator
    buggy: bool
    nodes: list[Node] = field(default_factory=list)
    primary: int = 0

    def primary_name(self) -> str:
        return self.nodes[self.primary].name

    def backup_name(self) -> str:
        return self.nodes[1 - self.primary].name

    def backup_alive(self) -> bool:
        return self.nodes[1 - self.primary].alive

    def crash_primary(self) -> None:
        node = self.nodes[self.primary]
        node.alive = False
        self.sim.log(f"CRASH {node.name} (ops awaiting backup ack: {sorted(node.pending)})")
        self.sim.schedule(self.sim.config.detect_delay, self.fail_over)

    def fail_over(self) -> None:
        old = self.nodes[self.primary]
        old.is_primary = False
        self.primary = 1 - self.primary
        new = self.nodes[self.primary]
        new.is_primary = True
        self.sim.log(f"FAILOVER {new.name} is primary with state "
                     f"{ {c: len(s) for c, s in sorted(new.state.items())} }")


@dataclass
class RunResult:
    seed: int
    ok: bool
    lost: list                      # acknowledged (op, counter) pairs missing at the end
    acked: int
    trace_hash: str
    trace: list
    config: SwarmConfig


def run(seed: int, buggy: bool = True, config: SwarmConfig | None = None,
        trace: bool = False) -> RunResult:
    """Run one seeded simulation and check the invariant."""
    config = config or SwarmConfig.from_seed(seed)
    sim = Simulator(seed, config, trace=trace)
    cluster = Cluster(sim, buggy)
    node_cls = BuggyNode if buggy else Node
    cluster.nodes = [node_cls(sim, "n0", cluster), node_cls(sim, "n1", cluster)]
    cluster.nodes[0].is_primary = True
    for n in cluster.nodes:
        sim.nodes[n.name] = n

    op_ids = iter(range(1, 10_000))
    clients = []
    for i in range(config.clients):
        ops = [(next(op_ids), f"c{sim.rng.randrange(config.counters)}")
               for _ in range(config.ops_per_client)]
        c = Client(sim, f"client{i}", cluster, ops)
        sim.nodes[c.name] = c
        clients.append(c)
        c.start()
    if config.crash_primary:
        sim.schedule(sim.rng.uniform(*config.crash_window), cluster.crash_primary)

    sim.run()

    final = cluster.nodes[cluster.primary]
    acked = [a for c in clients for a in c.acked]
    lost = [(op, counter) for op, counter in acked if not final.has(counter, op)]
    sim.log(f"END primary={final.name} acked={len(acked)} lost={lost}")
    return RunResult(seed, not lost, lost, len(acked), sim.trace_hash, sim.trace, config)
