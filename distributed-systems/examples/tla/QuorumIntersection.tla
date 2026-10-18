------------------------- MODULE QuorumIntersection -------------------------
(***************************************************************************)
(* Quorum intersection: why R + W > N gives you up-to-date reads.          *)
(*                                                                         *)
(* A key is replicated on N nodes.  A WRITE succeeds once W nodes have     *)
(* stored the new version; a READ asks R nodes and returns the highest     *)
(* version it sees.  A set of W nodes is a "write quorum", a set of R      *)
(* nodes a "read quorum".  Dynamo-style stores (Cassandra, Riak, the       *)
(* original Amazon Dynamo) let operators choose N, R and W.                *)
(*                                                                         *)
(* Claim: if R + W > N, then every read quorum shares at least one node    *)
(* with every write quorum (pigeonhole: R + W nodes cannot fit into N      *)
(* slots without overlap), so every read sees the latest completed write.  *)
(*                                                                         *)
(* This spec checks the claim two ways:                                    *)
(*   QuorumsIntersect    - the read quorum just used overlaps the write    *)
(*                         quorum used by the latest write.  Because TLC   *)
(*                         tries every possible quorum for every read and  *)
(*                         write, this covers every pair of quorums;       *)
(*   ReadSeesLatestWrite - the behavioural consequence: no read ever       *)
(*                         returns a version older than the newest one     *)
(*                         whose write had completed when the read ran.    *)
(* AllQuorumsIntersect states the same set-theoretic fact directly over    *)
(* the constants.  It is not listed in the .cfg files because it contains  *)
(* no variables, and TLC treats such formulas as assumptions rather than   *)
(* invariants (it would print no trace, only "FALSE").                     *)
(*                                                                         *)
(* Simplifications (deliberate, to keep the model small): writes complete  *)
(* one at a time, so there are no concurrent or half-finished writes, and  *)
(* nodes never fail.  Real systems add sloppy quorums, hinted handoff and  *)
(* read repair, which this spec does not model.                            *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS N,          \* number of replicas
          R,          \* read quorum size
          W,          \* write quorum size
          MaxWrites   \* bound on the number of writes, to keep the model finite

ASSUME /\ N \in Nat \ {0}
       /\ R \in 1..N
       /\ W \in 1..N
       /\ MaxWrites \in Nat

Nodes == 1..N

\* All subsets of Nodes of exactly the given size.  SUBSET S is the set of
\* all subsets of S (the power set).
ReadQuorums  == {Q \in SUBSET Nodes : Cardinality(Q) = R}
WriteQuorums == {Q \in SUBSET Nodes : Cardinality(Q) = W}

\* The largest element of a non-empty finite set of numbers.
Max(S) == CHOOSE x \in S : \A y \in S : y =< x

VARIABLES
  version,   \* version[n] is the version number stored on node n
  latest,    \* the newest version whose write has completed
  lastWrite, \* the quorum used by the most recent write ({} before any)
  lastRead   \* a record of the most recent read, for checking

vars == <<version, latest, lastWrite, lastRead>>

TypeOK ==
  /\ version  \in [Nodes -> 0..MaxWrites]
  /\ latest   \in 0..MaxWrites
  /\ lastWrite \in SUBSET Nodes
  /\ lastRead \in [quorum : SUBSET Nodes, saw : 0..MaxWrites,
                   latest : 0..MaxWrites]

Init ==
  /\ version  = [n \in Nodes |-> 0]
  /\ latest   = 0
  /\ lastWrite = {}
  /\ lastRead = [quorum |-> {}, saw |-> 0, latest |-> 0]

\* A client writes version latest+1 to the nodes of some write quorum Q.
\* TLC tries EVERY write quorum, because of the \E in Next.
Write(Q) ==
  /\ latest < MaxWrites
  /\ latest'  = latest + 1
  /\ lastWrite' = Q
  /\ version' = [n \in Nodes |-> IF n \in Q THEN latest + 1 ELSE version[n]]
  /\ UNCHANGED lastRead

\* A client reads from some read quorum Q and keeps the highest version.
\* We also remember what the newest completed write was at that moment.
Read(Q) ==
  /\ lastRead' = [quorum |-> Q,
                  saw    |-> Max({version[n] : n \in Q}),
                  latest |-> latest]
  /\ UNCHANGED <<version, latest, lastWrite>>

Next ==
  \/ \E Q \in WriteQuorums : Write(Q)
  \/ \E Q \in ReadQuorums  : Read(Q)

Spec == Init /\ [][Next]_vars

(***************************************************************************)
(* Properties                                                              *)
(***************************************************************************)

\* The quorums actually used overlap (vacuously true before the first
\* write or read).
QuorumsIntersect ==
  \/ lastWrite = {}
  \/ lastRead.quorum = {}
  \/ lastRead.quorum \cap lastWrite # {}

\* The same fact, stated over all quorums at once (constant-level).
AllQuorumsIntersect ==
  \A rq \in ReadQuorums, wq \in WriteQuorums : rq \cap wq # {}

\* No read returns a stale value.
ReadSeesLatestWrite == lastRead.saw = lastRead.latest
=============================================================================
