------------------------------- MODULE DieHard -------------------------------
(***************************************************************************)
(* A warm-up spec: the water-jug puzzle from the film "Die Hard with a     *)
(* Vengeance" (1995).  You have a 3-gallon jug, a 5-gallon jug and a tap.  *)
(* Measure exactly 4 gallons.                                              *)
(*                                                                         *)
(* Why start here?  It shows the three ideas every later spec uses:        *)
(*                                                                         *)
(*   - a STATE is an assignment of values to the VARIABLES (here: how much *)
(*     water is in each jug);                                              *)
(*   - an ACTION is a formula relating the current state (unprimed         *)
(*     variables, e.g. big) to the next state (primed variables, e.g.      *)
(*     big');                                                              *)
(*   - an INVARIANT is a formula that must be true in every reachable      *)
(*     state.  TLC, the model checker, visits every reachable state and    *)
(*     prints a trace (a "counterexample") if the invariant is ever false. *)
(*                                                                         *)
(* The trick: we claim the invariant NotSolved ("the big jug never holds   *)
(* 4 gallons").  TLC proves us wrong, and the counterexample it prints is  *)
(* a shortest sequence of pours that solves the puzzle.  So for THIS spec  *)
(* a violation is the expected, happy outcome.                             *)
(*                                                                         *)
(* This is adapted from Leslie Lamport's well-known example in the TLA+    *)
(* Video Course and the tlaplus/Examples repository.                       *)
(***************************************************************************)
EXTENDS Naturals

VARIABLES small,  \* gallons in the 3-gallon jug
          big     \* gallons in the 5-gallon jug

vars == <<small, big>>

\* A type invariant: a sanity check that variables only take sensible values.
TypeOK == /\ small \in 0..3
          /\ big   \in 0..5

\* Initially both jugs are empty.
Init == /\ small = 0
        /\ big   = 0

\* The six things you can do.  Each is an action: it says what the next
\* state looks like.  Every variable must be given a next value (or be
\* declared UNCHANGED), otherwise TLC complains.
FillSmall  == /\ small' = 3
              /\ big'   = big

FillBig    == /\ big'   = 5
              /\ small' = small

EmptySmall == /\ small' = 0
              /\ big'   = big

EmptyBig   == /\ big'   = 0
              /\ small' = small

\* Pour from small into big until big is full or small is empty.
SmallToBig == IF big + small =< 5
                THEN /\ big'   = big + small
                     /\ small' = 0
                ELSE /\ big'   = 5
                     /\ small' = small - (5 - big)

\* Pour from big into small until small is full or big is empty.
BigToSmall == IF big + small =< 3
                THEN /\ small' = big + small
                     /\ big'   = 0
                ELSE /\ small' = 3
                     /\ big'   = big - (3 - small)

\* The next-state relation: any one of the six actions may happen next.
Next == \/ FillSmall  \/ FillBig
        \/ EmptySmall \/ EmptyBig
        \/ SmallToBig \/ BigToSmall

\* The whole specification: start in Init, then every step is a Next step
\* (or a "stuttering" step that leaves vars unchanged).
Spec == Init /\ [][Next]_vars

\* The "invariant" we expect TLC to break.  Its counterexample is the answer.
NotSolved == big # 4
=============================================================================
