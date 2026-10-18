--------------------------- MODULE TwoPhaseCommit ---------------------------
(***************************************************************************)
(* Two-phase commit (2PC), modelled on Leslie Lamport's TwoPhase spec      *)
(* (Lamport and Gray, "Consensus on Transaction Commit", 2006; also the    *)
(* TLA+ Video Course and the tlaplus/Examples repository).                 *)
(*                                                                         *)
(* The problem.  A transaction touches several databases, called RESOURCE  *)
(* MANAGERS (RMs).  Either every RM commits the transaction or every RM    *)
(* aborts it; a mix would leave the data inconsistent.  A TRANSACTION      *)
(* MANAGER (TM) coordinates:                                               *)
(*                                                                         *)
(*   Phase 1: each RM that is able to commit tells the TM "Prepared".      *)
(*            An RM may instead decide on its own to abort.                *)
(*   Phase 2: if every RM is prepared, the TM broadcasts "Commit";         *)
(*            the TM may instead broadcast "Abort" at any time before      *)
(*            deciding to commit.                                          *)
(*                                                                         *)
(* Messages are modelled as a SET that only grows.  Once sent, a message   *)
(* can be received any number of times, in any order, or never: that       *)
(* covers duplication, reordering and delay for free.                      *)
(*                                                                         *)
(* Properties checked:                                                     *)
(*   TypeOK      - every variable holds a value of the expected shape.     *)
(*   Consistency - SAFETY: no RM has committed while another has aborted.  *)
(*   Termination - LIVENESS (only under FairSpec): eventually every RM     *)
(*                 has committed or aborted.                               *)
(***************************************************************************)
CONSTANT RM            \* The set of resource managers, e.g. {r1, r2, r3}

VARIABLES
  rmState,     \* rmState[r] is the state of RM r
  tmState,     \* the TM's state: "init", "committed" or "aborted"
  tmPrepared,  \* the set of RMs from which the TM has received "Prepared"
  msgs         \* every message that has ever been sent

vars == <<rmState, tmState, tmPrepared, msgs>>

\* The set of all possible messages.  A "Prepared" message names its sender;
\* "Commit" and "Abort" are broadcast by the TM to everyone.
Messages ==
  [type : {"Prepared"}, rm : RM]  \cup  [type : {"Commit", "Abort"}]

TypeOK ==
  /\ rmState    \in [RM -> {"working", "prepared", "committed", "aborted"}]
  /\ tmState    \in {"init", "committed", "aborted"}
  /\ tmPrepared \subseteq RM
  /\ msgs       \subseteq Messages

Init ==
  /\ rmState    = [r \in RM |-> "working"]
  /\ tmState    = "init"
  /\ tmPrepared = {}
  /\ msgs       = {}

(***************************************************************************)
(* Transaction-manager actions                                             *)
(***************************************************************************)

\* The TM receives a "Prepared" message from RM r.
TMRcvPrepared(r) ==
  /\ tmState = "init"
  /\ [type |-> "Prepared", rm |-> r] \in msgs
  /\ tmPrepared' = tmPrepared \cup {r}
  /\ UNCHANGED <<rmState, tmState, msgs>>

\* The TM commits.  The guard tmPrepared = RM is the heart of 2PC: the TM
\* may commit only once EVERY RM has promised it can.
TMCommit ==
  /\ tmState = "init"
  /\ tmPrepared = RM
  /\ tmState' = "committed"
  /\ msgs' = msgs \cup {[type |-> "Commit"]}
  /\ UNCHANGED <<rmState, tmPrepared>>

\* The TM aborts (for example after a timeout).  Allowed any time before
\* it has committed.
TMAbort ==
  /\ tmState = "init"
  /\ tmState' = "aborted"
  /\ msgs' = msgs \cup {[type |-> "Abort"]}
  /\ UNCHANGED <<rmState, tmPrepared>>

(***************************************************************************)
(* Resource-manager actions                                                *)
(***************************************************************************)

\* RM r votes yes: it promises to commit if asked, and tells the TM.
RMPrepare(r) ==
  /\ rmState[r] = "working"
  /\ rmState' = [rmState EXCEPT ![r] = "prepared"]
  /\ msgs' = msgs \cup {[type |-> "Prepared", rm |-> r]}
  /\ UNCHANGED <<tmState, tmPrepared>>

\* RM r votes no.  It may only do this BEFORE it has prepared; once it has
\* promised, it must wait for the TM's decision.
RMChooseToAbort(r) ==
  /\ rmState[r] = "working"
  /\ rmState' = [rmState EXCEPT ![r] = "aborted"]
  /\ UNCHANGED <<tmState, tmPrepared, msgs>>

\* RM r learns that the TM committed.
RMRcvCommitMsg(r) ==
  /\ [type |-> "Commit"] \in msgs
  /\ rmState' = [rmState EXCEPT ![r] = "committed"]
  /\ UNCHANGED <<tmState, tmPrepared, msgs>>

\* RM r learns that the TM aborted.
RMRcvAbortMsg(r) ==
  /\ [type |-> "Abort"] \in msgs
  /\ rmState' = [rmState EXCEPT ![r] = "aborted"]
  /\ UNCHANGED <<tmState, tmPrepared, msgs>>

Next ==
  \/ TMCommit \/ TMAbort
  \/ \E r \in RM :
       TMRcvPrepared(r) \/ RMPrepare(r) \/ RMChooseToAbort(r)
         \/ RMRcvCommitMsg(r) \/ RMRcvAbortMsg(r)

\* Safety-only specification: anything allowed by Next may happen, and the
\* system may also stop at any time.
Spec == Init /\ [][Next]_vars

\* For liveness we must also say that the system does not simply stop.
\* WF_vars(Next) ("weak fairness") means: if some Next step stays possible,
\* one eventually happens.
FairSpec == Spec /\ WF_vars(Next)

(***************************************************************************)
(* Properties                                                              *)
(***************************************************************************)

\* SAFETY: something bad (a split decision) never happens.
Consistency ==
  \A r1, r2 \in RM : ~ /\ rmState[r1] = "aborted"
                       /\ rmState[r2] = "committed"

\* LIVENESS: something good (every RM decides) eventually happens.
\* <>P means "P is true at some point in the behaviour".
Termination ==
  <>(\A r \in RM : rmState[r] \in {"committed", "aborted"})
=============================================================================
