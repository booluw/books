---------------------------- MODULE RaftElection ----------------------------
(***************************************************************************)
(* Raft leader election, simplified.                                       *)
(*                                                                         *)
(* Based on Diego Ongaro and John Ousterhout, "In Search of an             *)
(* Understandable Consensus Algorithm" (USENIX ATC 2014), and Ongaro's     *)
(* full TLA+ spec of Raft.  This version keeps only leader election: no    *)
(* log replication, no log up-to-date check, no heartbeats.                *)
(*                                                                         *)
(* Vocabulary.                                                             *)
(*   TERM      - a logical epoch number.  Each election starts a new term. *)
(*               Terms let servers tell stale messages from fresh ones.    *)
(*   FOLLOWER  - a passive server that votes and waits.                    *)
(*   CANDIDATE - a server that has timed out and is asking for votes.      *)
(*   LEADER    - a candidate that received votes from a MAJORITY.          *)
(*   votedFor  - whom this server voted for in its current term.  Raft     *)
(*               stores it (with currentTerm) on disk before replying, so  *)
(*               a restart cannot make a server forget its vote.           *)
(*                                                                         *)
(* The rule that makes election safe: each server votes at most once per   *)
(* term, and a leader needs a majority.  Two majorities of the same        *)
(* cluster always share a server, and that server cannot have voted for    *)
(* both candidates.  So there is at most one leader per term.              *)
(*                                                                         *)
(* Faults modelled.  Messages live in a set that only grows: a message can *)
(* be delivered late, more than once, in any order, or never (that is      *)
(* message loss).  Servers can restart at any time, losing volatile state  *)
(* (role, votes received) but keeping persistent state (currentTerm,       *)
(* votedFor).                                                              *)
(*                                                                         *)
(* The constant Bug switches in a deliberate mistake:                      *)
(*   "None"        - correct Raft election.        ElectionSafety holds.   *)
(*   "VoteTwice"   - a server grants every request in its term, even if it *)
(*                   already voted.                 TLC finds two leaders. *)
(*   "ForgetVote"  - votedFor is NOT persisted, so a restart forgets it.   *)
(*                                                  TLC finds two leaders. *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Server,    \* the set of servers, e.g. {s1, s2, s3}
  Nil,       \* a model value meaning "voted for nobody"
  MaxTerm,   \* terms stop at MaxTerm, to keep the model finite
  Bug        \* "None", "VoteTwice" or "ForgetVote"

ASSUME /\ MaxTerm \in Nat \ {0}
       /\ Nil \notin Server
       /\ Bug \in {"None", "VoteTwice", "ForgetVote"}

VARIABLES
  currentTerm,   \* persistent: currentTerm[s] is s's latest known term
  votedFor,      \* persistent: whom s voted for in currentTerm[s], or Nil
  role,          \* volatile:   "Follower", "Candidate" or "Leader"
  votesGranted,  \* volatile:   the servers that voted for s in its term
  msgs,          \* every message ever sent
  elected        \* ghost: the set of <<term, server>> pairs that ever won

vars == <<currentTerm, votedFor, role, votesGranted, msgs, elected>>

Terms == 0..MaxTerm

\* A majority (quorum) is any set containing more than half the servers.
IsMajority(S) == 2 * Cardinality(S) > Cardinality(Server)

\* Message shapes.  RequestVote is broadcast (no destination); a Vote is a
\* granted vote addressed to one candidate.  Refusals are not sent: in
\* this model a refusal carries no information a candidate needs.
RequestVoteMsgs == [type : {"RequestVote"}, term : Terms, src : Server]
VoteMsgs        == [type : {"Vote"}, term : Terms, src : Server, dst : Server]

TypeOK ==
  /\ currentTerm  \in [Server -> Terms]
  /\ votedFor     \in [Server -> Server \cup {Nil}]
  /\ role         \in [Server -> {"Follower", "Candidate", "Leader"}]
  /\ votesGranted \in [Server -> SUBSET Server]
  /\ msgs         \subseteq (RequestVoteMsgs \cup VoteMsgs)
  /\ elected      \subseteq (Terms \X Server)

Init ==
  /\ currentTerm  = [s \in Server |-> 0]
  /\ votedFor     = [s \in Server |-> Nil]
  /\ role         = [s \in Server |-> "Follower"]
  /\ votesGranted = [s \in Server |-> {}]
  /\ msgs         = {}
  /\ elected      = {}

(***************************************************************************)
(* Actions                                                                 *)
(***************************************************************************)

\* Server s's election timer fires: it starts a new term, votes for itself
\* and asks everyone else for their vote.
Timeout(s) ==
  /\ role[s] \in {"Follower", "Candidate"}
  /\ currentTerm[s] < MaxTerm
  /\ currentTerm'  = [currentTerm  EXCEPT ![s] = currentTerm[s] + 1]
  /\ role'         = [role         EXCEPT ![s] = "Candidate"]
  /\ votedFor'     = [votedFor     EXCEPT ![s] = s]
  /\ votesGranted' = [votesGranted EXCEPT ![s] = {s}]
  /\ msgs' = msgs \cup {[type |-> "RequestVote",
                         term |-> currentTerm[s] + 1, src |-> s]}
  /\ UNCHANGED elected

\* Server s receives a RequestVote message m.
\*  1. If m carries a newer term, s adopts that term, becomes a follower
\*     and clears its vote (it has not voted in the new term yet).
\*  2. s grants its vote if the terms match and it has not already voted
\*     for someone else in this term.  (The Bug "VoteTwice" drops this
\*     second check.)
HandleRequestVote(s, m) ==
  /\ m \in msgs
  /\ m.type = "RequestVote"
  /\ m.src # s
  /\ LET newer   == m.term > currentTerm[s]
         term    == IF newer THEN m.term ELSE currentTerm[s]
         voted   == IF newer THEN Nil ELSE votedFor[s]
         grant   == /\ m.term = term
                    /\ \/ voted \in {Nil, m.src}
                       \/ Bug = "VoteTwice"
     IN /\ currentTerm'  = [currentTerm EXCEPT ![s] = term]
        /\ role'         = IF newer THEN [role EXCEPT ![s] = "Follower"]
                                    ELSE role
        /\ votesGranted' = IF newer THEN [votesGranted EXCEPT ![s] = {}]
                                    ELSE votesGranted
        /\ votedFor'     = [votedFor EXCEPT ![s] = IF grant THEN m.src
                                                           ELSE voted]
        /\ msgs' = IF grant
                     THEN msgs \cup {[type |-> "Vote", term |-> term,
                                      src |-> s, dst |-> m.src]}
                     ELSE msgs
  /\ UNCHANGED elected

\* Candidate s receives a vote for its current term.
HandleVote(s, m) ==
  /\ m \in msgs
  /\ m.type = "Vote"
  /\ m.dst = s
  /\ role[s] = "Candidate"
  /\ m.term = currentTerm[s]
  /\ votesGranted' = [votesGranted EXCEPT ![s] = @ \cup {m.src}]
  /\ UNCHANGED <<currentTerm, votedFor, role, msgs, elected>>

\* A candidate with votes from a majority becomes leader.  We also record
\* the win in the ghost variable elected, so that ElectionSafety can talk
\* about leaders who have since stepped down.
BecomeLeader(s) ==
  /\ role[s] = "Candidate"
  /\ IsMajority(votesGranted[s])
  /\ role'    = [role EXCEPT ![s] = "Leader"]
  /\ elected' = elected \cup {<<currentTerm[s], s>>}
  /\ UNCHANGED <<currentTerm, votedFor, votesGranted, msgs>>

\* Server s crashes and restarts.  Volatile state is lost; persistent state
\* survives, unless the Bug "ForgetVote" is on.
Restart(s) ==
  /\ role'         = [role         EXCEPT ![s] = "Follower"]
  /\ votesGranted' = [votesGranted EXCEPT ![s] = {}]
  /\ votedFor'     = IF Bug = "ForgetVote"
                       THEN [votedFor EXCEPT ![s] = Nil]
                       ELSE votedFor
  /\ UNCHANGED <<currentTerm, msgs, elected>>

\* Wrapping the "pick any message" choice in a named operator makes TLC
\* print the operator's name in counterexample traces.
ReceiveRequestVote(s) == \E m \in msgs : HandleRequestVote(s, m)
ReceiveVote(s)        == \E m \in msgs : HandleVote(s, m)

Next ==
  \E s \in Server :
    \/ Timeout(s)
    \/ ReceiveRequestVote(s)
    \/ ReceiveVote(s)
    \/ BecomeLeader(s)
    \/ Restart(s)

Spec == Init /\ [][Next]_vars

\* Servers are interchangeable, so TLC may treat states that differ only by
\* renaming servers as the same state.  This "symmetry reduction" shrinks
\* the state space; it is sound for safety properties like ours.
Symmetry == Permutations(Server)

(***************************************************************************)
(* Properties                                                              *)
(***************************************************************************)

\* ELECTION SAFETY (Raft paper, Figure 3): at most one leader per term.
ElectionSafety ==
  \A e1, e2 \in elected : e1[1] = e2[1] => e1[2] = e2[2]

\* A sanity check on the model itself: a correct spec that never elects
\* anybody would satisfy ElectionSafety trivially.  Listing this invariant
\* (see the README's experiments) makes TLC show a run where a leader IS
\* elected, proving the interesting states are reachable.
NoLeaderEver == elected = {}
=============================================================================
