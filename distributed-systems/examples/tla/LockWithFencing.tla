--------------------------- MODULE LockWithFencing ---------------------------
(***************************************************************************)
(* A lease-based lock, a client that pauses, and fencing tokens.           *)
(*                                                                         *)
(* Based on Martin Kleppmann, "How to do distributed locking" (2016).      *)
(*                                                                         *)
(* The setting.  Several clients want exclusive access to a storage        *)
(* service.  A LOCK SERVICE hands out a LEASE: a lock that expires on its  *)
(* own after LeaseDuration clock ticks, so that a crashed client cannot    *)
(* hold the lock forever.  Before writing, a careful client checks that    *)
(* its lease has not expired.                                              *)
(*                                                                         *)
(* The problem.  Between "check my lease" and "my write reaches storage",  *)
(* the client can PAUSE: a garbage-collection stop-the-world pause, a page *)
(* fault, a slow network.  Meanwhile the lease expires, another client     *)
(* gets the lock and writes, and then the paused client's write arrives    *)
(* and overwrites newer data.  No amount of checking inside the client     *)
(* closes that gap, because the pause can happen after the check.          *)
(*                                                                         *)
(* The fix.  Every grant carries a FENCING TOKEN, a number that increases  *)
(* by one with each grant.  The client sends its token with each write,    *)
(* and storage remembers the highest token it has seen and REJECTS any     *)
(* write carrying a lower one.  The check moves to the one place that sees *)
(* writes in their real order: the storage service.                        *)
(*                                                                         *)
(* How time is modelled.  There is one global clock that only goes up     *)
(* (action Tick).  A client "pauses" simply by taking no steps while other *)
(* actions, including Tick, happen.  TLC tries every interleaving, so it   *)
(* tries every possible pause.  There is no clock skew: even with perfect  *)
(* clocks, pauses alone break the unfenced version.                        *)
(*                                                                         *)
(* UseFencing = TRUE  : storage checks tokens   -> NoStaleWrite holds.     *)
(* UseFencing = FALSE : storage ignores tokens  -> TLC finds a stale write.*)
(***************************************************************************)
EXTENDS Naturals, Sequences

CONSTANTS
  Clients,        \* the set of clients, e.g. {c1, c2}
  Nobody,         \* a model value meaning "no client"
  LeaseDuration,  \* how many ticks a lease lasts
  MaxTime,        \* the clock stops at MaxTime, to keep the model finite
  UseFencing      \* TRUE: storage checks fencing tokens; FALSE: it does not

ASSUME /\ LeaseDuration \in Nat \ {0}
       /\ MaxTime \in Nat
       /\ UseFencing \in BOOLEAN
       /\ Nobody \notin Clients

VARIABLES
  clock,          \* the global clock
  lockOwner,      \* lock service: the client holding the latest grant
  leaseExpiry,    \* lock service: the time at which the latest grant expires
  latestToken,    \* lock service: the token of the latest grant (0 = none)
  clientState,    \* clientState[c] \in {"idle", "holding", "writing"}
  clientToken,    \* the token client c received with its lease
  clientExpiry,   \* when client c believes its lease expires
  storageToken,   \* storage: the highest token it has accepted a write from
  writeLog        \* ghost variable: the sequence of accepted writes

\* A "ghost" (or "history") variable exists only to state a property; the
\* real system would not need it.  Each entry records the writer's token
\* and the latest token the lock service had granted at the moment the
\* write was accepted.

vars == <<clock, lockOwner, leaseExpiry, latestToken, clientState,
          clientToken, clientExpiry, storageToken, writeLog>>

MaxToken == MaxTime + 1   \* a generous bound used only by TypeOK

TypeOK ==
  /\ clock        \in 0..MaxTime
  /\ lockOwner    \in Clients \cup {Nobody}
  /\ leaseExpiry  \in 0..(MaxTime + LeaseDuration)
  /\ latestToken  \in 0..MaxToken
  /\ clientState  \in [Clients -> {"idle", "holding", "writing"}]
  /\ clientToken  \in [Clients -> 0..MaxToken]
  /\ clientExpiry \in [Clients -> 0..(MaxTime + LeaseDuration)]
  /\ storageToken \in 0..MaxToken
  /\ writeLog     \in Seq([writer : Clients, token : 0..MaxToken,
                           latest : 0..MaxToken])

Init ==
  /\ clock        = 0
  /\ lockOwner    = Nobody
  /\ leaseExpiry  = 0
  /\ latestToken  = 0
  /\ clientState  = [c \in Clients |-> "idle"]
  /\ clientToken  = [c \in Clients |-> 0]
  /\ clientExpiry = [c \in Clients |-> 0]
  /\ storageToken = 0
  /\ writeLog     = <<>>

(***************************************************************************)
(* Actions                                                                 *)
(***************************************************************************)

\* Time passes.
Tick ==
  /\ clock < MaxTime
  /\ clock' = clock + 1
  /\ UNCHANGED <<lockOwner, leaseExpiry, latestToken, clientState,
                 clientToken, clientExpiry, storageToken, writeLog>>

\* The lock service grants a lease to client c.  It does so only when the
\* previous lease has expired (or there never was one).  Each grant gets
\* the next fencing token.
Acquire(c) ==
  /\ clientState[c] = "idle"
  /\ clock >= leaseExpiry
  /\ latestToken'  = latestToken + 1
  /\ lockOwner'    = c
  /\ leaseExpiry'  = clock + LeaseDuration
  /\ clientState'  = [clientState  EXCEPT ![c] = "holding"]
  /\ clientToken'  = [clientToken  EXCEPT ![c] = latestToken + 1]
  /\ clientExpiry' = [clientExpiry EXCEPT ![c] = clock + LeaseDuration]
  /\ UNCHANGED <<clock, storageToken, writeLog>>

\* A careful client checks that its lease is still valid and then sends its
\* write.  After this step the write is "in flight": the client may now be
\* paused for any amount of time before the write reaches storage.
StartWrite(c) ==
  /\ clientState[c] = "holding"
  /\ clock < clientExpiry[c]
  /\ clientState' = [clientState EXCEPT ![c] = "writing"]
  /\ UNCHANGED <<clock, lockOwner, leaseExpiry, latestToken, clientToken,
                 clientExpiry, storageToken, writeLog>>

\* A client notices its lease has expired before writing, and gives up.
GiveUp(c) ==
  /\ clientState[c] = "holding"
  /\ clock >= clientExpiry[c]
  /\ clientState' = [clientState EXCEPT ![c] = "idle"]
  /\ UNCHANGED <<clock, lockOwner, leaseExpiry, latestToken, clientToken,
                 clientExpiry, storageToken, writeLog>>

\* Client c's write arrives at storage.  With fencing, storage accepts it
\* only if its token is at least the highest token storage has seen.
\* Without fencing, storage accepts everything.
Accept(c) ==
  \/ ~UseFencing
  \/ clientToken[c] >= storageToken

WriteArrives(c) ==
  /\ clientState[c] = "writing"
  /\ clientState' = [clientState EXCEPT ![c] = "idle"]
  /\ IF Accept(c)
       THEN /\ storageToken' = IF clientToken[c] > storageToken
                                 THEN clientToken[c] ELSE storageToken
            /\ writeLog' = Append(writeLog,
                                  [writer |-> c, token |-> clientToken[c],
                                   latest |-> latestToken])
       ELSE UNCHANGED <<storageToken, writeLog>>   \* rejected
  /\ UNCHANGED <<clock, lockOwner, leaseExpiry, latestToken, clientToken,
                 clientExpiry>>

Next ==
  \/ Tick
  \/ \E c \in Clients :
       Acquire(c) \/ StartWrite(c) \/ GiveUp(c) \/ WriteArrives(c)

Spec == Init /\ [][Next]_vars

(***************************************************************************)
(* Properties                                                              *)
(***************************************************************************)

\* The main safety property.  Storage never accepts a write from a client
\* whose lease has been superseded by a newer grant whose holder has
\* already written.  Equivalently: accepted writes carry non-decreasing
\* tokens, so an old lease holder can never overwrite a newer one's data.
NoStaleWrite ==
  \A i \in 1..(Len(writeLog) - 1) :
    writeLog[i].token =< writeLog[i + 1].token

\* A STRONGER property: every accepted write comes from the holder of the
\* latest grant at that moment.  Fencing does NOT guarantee this: if the
\* old holder's delayed write reaches storage after a new lease is granted
\* but before the new holder has written anything, storage has no way to
\* know the token is stale.  The data is still safe (the new holder's
\* later write supersedes it and the old holder can never write after
\* it), which is exactly what NoStaleWrite says.  Try adding this to the
\* .cfg: TLC shows the gap.
OnlyLatestHolderWrites ==
  \A i \in 1..Len(writeLog) : writeLog[i].token = writeLog[i].latest
=============================================================================
