"""Raft's safety properties, checked after every simulation step (Chapter 11).

Figure 3 of the Raft paper lists the properties the algorithm guarantees.
The checker observes every server after every event and keeps *ghost
state* (information no real server has, such as every commit ever seen)
to check them:

* **Election Safety:** at most one leader is elected in a given term.
* **Log Matching:** if two logs contain an entry with the same index and
  term, the logs are identical in all entries up to that index.
* **Leader Completeness:** if an entry is committed in a given term, it is
  present in the logs of the leaders of all higher-numbered terms.
* **State Machine Safety:** if a server has applied an entry at a given
  index, no other server ever applies a different entry at that index.
  We also check the stronger statement that servers never *commit*
  different entries at the same index.

(The fifth property, Leader Append-Only, holds by construction here: the
code has no path by which a leader removes entries from its own log.)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from raft import LEADER, Entry


@dataclass
class Violation:
    invariant: str
    time: float
    detail: str

    def __str__(self) -> str:
        return f"t={self.time:.1f}ms {self.invariant}: {self.detail}"


def _short(entry: Entry) -> str:
    c = entry.command
    what = "no-op" if c is None else f"{c.op} {c.key}={c.value}"
    return f"term-{entry.term} entry ({what})"


class InvariantViolation(AssertionError):
    def __init__(self, violation: Violation) -> None:
        super().__init__(str(violation))
        self.violation = violation


class InvariantChecker:
    def __init__(self, nodes: Dict[str, "RaftNode"], stop_on_violation: bool = True) -> None:
        self.nodes = nodes
        self.stop_on_violation = stop_on_violation
        self.violations: List[Violation] = []
        self.checks = 0
        # Ghost state.
        self.leader_of_term: Dict[int, str] = {}
        self.committed: Dict[int, Tuple[Entry, int, str]] = {}   # index -> (entry, term, by)
        self.applied: Dict[int, Tuple[Entry, str]] = {}
        self._seen_commit = {n: 0 for n in nodes}
        self._seen_applied = {n: 0 for n in nodes}
        self._seen_incarnation = {n: node.incarnation for n, node in nodes.items()}
        self._log_versions: Dict[str, int] = {}
        self._completeness_key = None

    def _fail(self, now: float, invariant: str, detail: str) -> None:
        violation = Violation(invariant, now, detail)
        if violation not in self.violations:
            self.violations.append(violation)
        if self.stop_on_violation:
            raise InvariantViolation(violation)

    def check(self, now: float = 0.0) -> None:
        self.checks += 1
        self.check_election_safety(now)
        self.check_commits_and_applies(now)
        self.check_log_matching(now)
        self.check_leader_completeness(now)

    # ------------------------------------------------------------------------
    def check_election_safety(self, now: float) -> None:
        for node in self.nodes.values():
            if node.alive and node.role == LEADER:
                first = self.leader_of_term.setdefault(node.current_term, node.id)
                if first != node.id:
                    self._fail(now, "Election Safety",
                               f"{first} and {node.id} both leader in term {node.current_term}")

    def check_commits_and_applies(self, now: float) -> None:
        for node in self.nodes.values():
            if node.incarnation != self._seen_incarnation[node.id]:
                # Crashed since we last looked: its volatile state starts again from 0.
                self._seen_incarnation[node.id] = node.incarnation
                self._seen_commit[node.id] = 0
                self._seen_applied[node.id] = 0
            for i in range(self._seen_commit[node.id] + 1, node.commit_index + 1):
                entry = node.log[i - 1]
                if i in self.committed and self.committed[i][0] != entry:
                    other, term, by = self.committed[i]
                    self._fail(now, "State Machine Safety",
                               f"index {i} committed as term-{other.term} entry by {by} "
                               f"and as term-{entry.term} entry by {node.id}")
                self.committed.setdefault(i, (entry, node.current_term, node.id))
            self._seen_commit[node.id] = node.commit_index
            for i in range(self._seen_applied[node.id] + 1, node.last_applied + 1):
                entry = node.log[i - 1]
                if i in self.applied and self.applied[i][0] != entry:
                    other, by = self.applied[i]
                    self._fail(now, "State Machine Safety",
                               f"index {i} applied as {_short(other)} by {by} "
                               f"and as {_short(entry)} by {node.id}")
                self.applied.setdefault(i, (entry, node.id))
            self._seen_applied[node.id] = node.last_applied

    def check_log_matching(self, now: float) -> None:
        versions = {n: node.storage.version for n, node in self.nodes.items()}
        if versions == self._log_versions:
            return                                   # no log changed: nothing new to check
        self._log_versions = versions
        nodes = list(self.nodes.values())
        for a in range(len(nodes)):
            for b in range(a + 1, len(nodes)):
                x, y = nodes[a].log, nodes[b].log
                # Find the highest index where both logs have the same term;
                # everything up to it must be identical.
                i = min(len(x), len(y))
                while i > 0 and x[i - 1].term != y[i - 1].term:
                    i -= 1
                if x[:i] != y[:i]:
                    j = next(k for k in range(i) if x[k] != y[k])
                    self._fail(now, "Log Matching",
                               f"{nodes[a].id} and {nodes[b].id} agree on term at index {i} "
                               f"but differ at index {j + 1}")

    def check_leader_completeness(self, now: float) -> None:
        leaders = [n for n in self.nodes.values() if n.alive and n.role == LEADER]
        key = (len(self.committed), tuple((n.id, n.current_term, n.storage.version) for n in leaders))
        if key == self._completeness_key:
            return
        self._completeness_key = key
        for leader in leaders:
            for index, (entry, term, by) in self.committed.items():
                if term <= leader.current_term and (
                        index > leader.last_index() or leader.log[index - 1] != entry):
                    self._fail(now, "Leader Completeness",
                               f"{leader.id}, leader in term {leader.current_term}, lacks entry "
                               f"{index} (term {entry.term}) committed in term {term} by {by}")
