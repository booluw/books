"""A Raft server, following Figure 2 of Ongaro and Ousterhout (2014).

Raft keeps a replicated *log* of commands identical on a majority of
servers, and applies committed commands, in log order, to a *state
machine* (here, a key-value store). It splits the problem into:

* **Leader election.** Every server starts as a *follower*. A follower
  that hears nothing from a leader for a randomised *election timeout*
  becomes a *candidate*: it increments its *term* (a logical clock that
  numbers elections), votes for itself and asks the others. A majority of
  votes makes it *leader* for that term. Randomised timeouts make split
  votes rare.
* **Log replication.** The leader appends client commands to its log and
  sends them in ``AppendEntries`` messages, each carrying the index and
  term of the entry just before the new ones. A follower accepts only if
  its log has that entry (the *consistency check*); otherwise the leader
  backs up and retries. This keeps logs identical up to the last matching
  entry (*Log Matching*).
* **Safety.** A server votes only for a candidate whose log is at least as
  up to date as its own, and a leader counts replicas to commit only
  entries from its *current* term (the Figure 8 rule). Together these
  ensure every future leader has every committed entry (*Leader
  Completeness*).

Persistent state (``current_term``, ``voted_for`` and ``log``) lives in a
:class:`Storage` object that survives :meth:`RaftNode.crash`. In this
simulation a message handler runs atomically, so "write to disk before
replying" holds automatically; a real server must fsync before it answers.

Two deliberate bugs can be switched on through ``bugs``:

* ``"vote_without_log_check"``: grant votes without the up-to-date check;
* ``"commit_previous_term"``: commit any entry stored on a majority,
  whatever its term (the mistake Figure 8 of the paper warns about).
"""

import random
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

FOLLOWER, CANDIDATE, LEADER = "follower", "candidate", "leader"
KNOWN_BUGS = frozenset({"vote_without_log_check", "commit_previous_term"})


# ---------------------------------------------------------------------------
# Log entries and messages
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Command:
    client: str
    seq: int          # per-client sequence number, for exactly-once application
    op: str           # "put" or "get"
    key: str
    value: Any = None


@dataclass(frozen=True)
class Entry:
    term: int
    command: Optional[Command]   # None for a leader's no-op entry


@dataclass(frozen=True)
class RequestVote:
    term: int
    candidate: str
    last_log_index: int
    last_log_term: int


@dataclass(frozen=True)
class RequestVoteReply:
    term: int
    granted: bool


@dataclass(frozen=True)
class AppendEntries:
    term: int
    leader: str
    prev_log_index: int
    prev_log_term: int
    entries: Tuple[Entry, ...]
    leader_commit: int


@dataclass(frozen=True)
class AppendEntriesReply:
    term: int
    success: bool
    match_index: int     # on success: last index known to match the leader
    hint: int            # on failure: where the leader should try next


@dataclass(frozen=True)
class ClientRequest:
    command: Command


@dataclass(frozen=True)
class ClientReply:
    seq: int
    ok: bool
    result: Any = None
    leader_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Durable storage and the state machine
# ---------------------------------------------------------------------------

@dataclass
class Storage:
    """What a server writes to disk. Survives crashes."""

    current_term: int = 0
    voted_for: Optional[str] = None
    log: List[Entry] = field(default_factory=list)   # log[i - 1] is entry i
    version: int = 0      # bumped on every log change; lets checkers skip work


class KVStateMachine:
    """A key-value store. Remembers each client's last sequence number so a
    retried command that was committed twice is applied only once."""

    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.last_seq: Dict[str, Tuple[int, Any]] = {}

    def apply(self, command: Optional[Command]) -> Any:
        if command is None:
            return None
        seen = self.last_seq.get(command.client)
        if seen and seen[0] >= command.seq:
            return seen[1]                      # duplicate: return the first result
        if command.op == "put":
            self.data[command.key] = command.value
            result = command.value
        else:
            result = self.data.get(command.key)
        self.last_seq[command.client] = (command.seq, result)
        return result


@dataclass
class RaftConfig:
    election_timeout: tuple = (150.0, 300.0)   # ms, chosen afresh each time
    heartbeat_interval: float = 50.0
    max_batch: int = 20                        # entries per AppendEntries
    noop_on_election: bool = False             # Raft paper section 8


# ---------------------------------------------------------------------------
# The server
# ---------------------------------------------------------------------------

class RaftNode:
    def __init__(self, node_id: str, peers: List[str], scheduler, network,
                 rng: random.Random, config: Optional[RaftConfig] = None,
                 bugs: FrozenSet[str] = frozenset()) -> None:
        unknown = set(bugs) - KNOWN_BUGS
        if unknown:
            raise ValueError(f"unknown bugs {unknown}; choose from {sorted(KNOWN_BUGS)}")
        self.id = node_id
        self.peers = [p for p in peers if p != node_id]
        self.scheduler = scheduler
        self.network = network
        self.rng = rng
        self.config = config or RaftConfig()
        self.bugs = frozenset(bugs)
        self.storage = Storage()
        self.alive = True
        self.incarnation = 0     # bumped on crash, so timers set before it are ignored
        self._reset_volatile()

    # -- persistent state, read through to storage --------------------------
    @property
    def current_term(self) -> int:
        return self.storage.current_term

    @property
    def voted_for(self) -> Optional[str]:
        return self.storage.voted_for

    @property
    def log(self) -> List[Entry]:
        return self.storage.log

    def last_index(self) -> int:
        return len(self.log)

    def term_at(self, index: int) -> int:
        return self.log[index - 1].term if index > 0 else 0

    def majority(self) -> int:
        return (len(self.peers) + 1) // 2 + 1

    # -- volatile state ----------------------------------------------------
    def _reset_volatile(self) -> None:
        self.role = FOLLOWER
        self.leader_id: Optional[str] = None
        self.commit_index = 0
        self.last_applied = 0
        self.state_machine = KVStateMachine()
        self.votes: Set[str] = set()
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        self.pending_clients: Dict[int, Tuple[str, int]] = {}   # log index -> (client, seq)
        self._timer_generation = 0

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        self._reset_election_timer()

    def crash(self) -> None:
        """Lose everything except ``storage``."""
        self.alive = False
        self.incarnation += 1
        self._reset_volatile()

    def restart(self) -> None:
        self.alive = True
        self._reset_volatile()
        self.start()

    # -- timers ---------------------------------------------------------------
    def _timer(self, delay: float, callback) -> None:
        incarnation, generation = self.incarnation, self._timer_generation

        def fire():
            if self.alive and self.incarnation == incarnation and \
                    self._timer_generation == generation:
                callback()
        self.scheduler.after(delay, fire)

    def _reset_election_timer(self) -> None:
        self._timer_generation += 1     # cancels any earlier timer
        self._timer(self.rng.uniform(*self.config.election_timeout), self.on_election_timeout)

    # -- persistent state changes -------------------------------------------
    def _set_term(self, term: int) -> None:
        self.storage.current_term = term
        self.storage.voted_for = None

    def _vote(self, candidate: str) -> None:
        self.storage.voted_for = candidate

    def _append(self, entry: Entry) -> None:
        self.storage.log.append(entry)
        self.storage.version += 1

    def _truncate(self, last_kept: int) -> None:
        del self.storage.log[last_kept:]
        self.storage.version += 1

    # -- messaging ----------------------------------------------------------
    def send(self, dst: str, msg) -> None:
        self.network.send(self.id, dst, msg)

    def receive(self, src: str, msg) -> None:
        if not self.alive:
            return
        handler = {
            RequestVote: self.on_request_vote,
            RequestVoteReply: self.on_request_vote_reply,
            AppendEntries: self.on_append_entries,
            AppendEntriesReply: self.on_append_entries_reply,
            ClientRequest: self.on_client_request,
        }[type(msg)]
        handler(src, msg)

    def _step_down(self, term: int) -> None:
        """Seeing a higher term means our information is stale: become a follower."""
        if term > self.current_term:
            self._set_term(term)
        if self.role != FOLLOWER:
            self.role = FOLLOWER
            self.pending_clients.clear()
            self._reset_election_timer()

    # -- leader election ----------------------------------------------------
    def on_election_timeout(self) -> None:
        if self.role == LEADER:
            return
        self.role = CANDIDATE
        self.leader_id = None
        self._set_term(self.current_term + 1)
        self._vote(self.id)
        self.votes = {self.id}
        self._reset_election_timer()            # try again if this election fails
        request = RequestVote(self.current_term, self.id, self.last_index(),
                              self.term_at(self.last_index()))
        for peer in self.peers:
            self.send(peer, request)

    def log_up_to_date(self, last_index: int, last_term: int) -> bool:
        """Raft section 5.4.1: compare last terms, then lengths."""
        my_term = self.term_at(self.last_index())
        return last_term > my_term or (last_term == my_term and last_index >= self.last_index())

    def on_request_vote(self, src: str, m: RequestVote) -> None:
        if m.term > self.current_term:
            self._step_down(m.term)
        up_to_date = self.log_up_to_date(m.last_log_index, m.last_log_term)
        if "vote_without_log_check" in self.bugs:
            up_to_date = True                    # BUG: any candidate will do
        granted = (m.term == self.current_term
                   and self.voted_for in (None, m.candidate)
                   and up_to_date)
        if granted:
            self._vote(m.candidate)
            self._reset_election_timer()
        self.send(src, RequestVoteReply(self.current_term, granted))

    def on_request_vote_reply(self, src: str, m: RequestVoteReply) -> None:
        if m.term > self.current_term:
            self._step_down(m.term)
            return
        if self.role != CANDIDATE or m.term != self.current_term or not m.granted:
            return
        self.votes.add(src)
        if len(self.votes) >= self.majority():
            self._become_leader()

    def _become_leader(self) -> None:
        self.role = LEADER
        self.leader_id = self.id
        self.next_index = {p: self.last_index() + 1 for p in self.peers}
        self.match_index = {p: 0 for p in self.peers}
        if self.config.noop_on_election:
            self._append(Entry(self.current_term, None))
        self._heartbeat()

    def _heartbeat(self) -> None:
        if self.role != LEADER:
            return
        for peer in self.peers:
            self.send_append(peer)
        self._timer_generation += 1              # no election timer while leading
        self._timer(self.config.heartbeat_interval, self._heartbeat)

    # -- log replication ----------------------------------------------------
    def propose(self, command: Optional[Command]) -> int:
        """Leader only: append a command to the local log; returns its index."""
        assert self.role == LEADER
        self._append(Entry(self.current_term, command))
        return self.last_index()

    def send_append(self, peer: str) -> None:
        prev = self.next_index[peer] - 1
        entries = tuple(self.log[prev:prev + self.config.max_batch])
        self.send(peer, AppendEntries(self.current_term, self.id, prev, self.term_at(prev),
                                      entries, self.commit_index))

    def on_append_entries(self, src: str, m: AppendEntries) -> None:
        if m.term < self.current_term:
            self.send(src, AppendEntriesReply(self.current_term, False, 0, 0))
            return
        self._step_down(m.term)                  # a valid leader exists for this term
        self.leader_id = m.leader
        self._reset_election_timer()
        # Consistency check: do we hold the entry just before the new ones?
        if m.prev_log_index > self.last_index():
            self.send(src, AppendEntriesReply(self.current_term, False, 0, self.last_index() + 1))
            return
        if self.term_at(m.prev_log_index) != m.prev_log_term:
            self.send(src, AppendEntriesReply(self.current_term, False, 0, m.prev_log_index))
            return
        # Append, deleting a conflicting suffix only where terms differ. An old,
        # duplicated or reordered message must never truncate newer entries.
        index = m.prev_log_index
        for entry in m.entries:
            index += 1
            if index <= self.last_index():
                if self.term_at(index) == entry.term:
                    continue
                self._truncate(index - 1)
            self._append(entry)
        last_new = m.prev_log_index + len(m.entries)
        if m.leader_commit > self.commit_index:
            self.commit_index = min(m.leader_commit, last_new)
            self._apply_committed()
        self.send(src, AppendEntriesReply(self.current_term, True, last_new, 0))

    def on_append_entries_reply(self, src: str, m: AppendEntriesReply) -> None:
        if m.term > self.current_term:
            self._step_down(m.term)
            return
        if self.role != LEADER or m.term != self.current_term:
            return                               # stale reply from an earlier term
        if m.success:
            self.match_index[src] = max(self.match_index[src], m.match_index)
            self.next_index[src] = max(self.next_index[src], self.match_index[src] + 1)
            self._advance_commit_index()
            if self.next_index[src] <= self.last_index():
                self.send_append(src)            # more to send
        else:
            self.next_index[src] = max(1, min(self.next_index[src] - 1, m.hint or self.next_index[src] - 1))
            self.send_append(src)

    def _advance_commit_index(self) -> None:
        """Commit the highest index stored on a majority, *if it is from this term*."""
        for n in range(self.last_index(), self.commit_index, -1):
            if self.term_at(n) != self.current_term and "commit_previous_term" not in self.bugs:
                continue                         # Figure 8: never count replicas for old terms
            replicas = 1 + sum(1 for p in self.peers if self.match_index[p] >= n)
            if replicas >= self.majority():
                self.commit_index = n
                self._apply_committed()
                return

    def _apply_committed(self) -> None:
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            result = self.state_machine.apply(entry.command)
            waiting = self.pending_clients.pop(self.last_applied, None)
            if waiting and self.role == LEADER:
                client, seq = waiting
                self.send(client, ClientReply(seq, True, result))

    # -- clients ------------------------------------------------------------
    def on_client_request(self, src: str, m: ClientRequest) -> None:
        if self.role != LEADER:
            self.send(src, ClientReply(m.command.seq, False, leader_hint=self.leader_id))
            return
        index = self.propose(m.command)
        self.pending_clients[index] = (src, m.command.seq)
        for peer in self.peers:
            self.send_append(peer)

    def describe(self) -> str:
        log = " ".join(str(e.term) for e in self.log)
        status = self.role if self.alive else "DOWN"
        return (f"{self.id} {status:<9} term={self.current_term:<3} "
                f"commit={self.commit_index:<3} log=[{log}]")
