# Two-phase commit and sagas (Chapter 9)

## The problem

An order touches three systems: the order database, the payment service and the inventory service. Either all three record the order, or none does. On one database, a transaction gives you that for free. Across machines, any of them can crash at any moment, and messages can be lost. This example builds the two standard answers and breaks each one on purpose:

- **Two-phase commit (2PC)** (`twopc.py`) gives true atomicity, at the price of **blocking**: if the coordinator crashes at the wrong moment, participants hold their locks and wait, possibly for a long time.
- **Sagas** (`saga.py`) never block. They commit each step immediately and undo completed steps with **compensating actions** if a later step fails. The price is **isolation**: other readers can see half-finished work.

## Terms

- **Atomicity:** all of a transaction's effects happen, or none do.
- **Isolation:** concurrent transactions do not see each other's intermediate states.
- **Coordinator** (or transaction manager): the node that runs 2PC and makes the commit decision.
- **Participant** (or resource manager): a node that owns some of the data and votes.
- **Durable log:** an append-only file flushed to disk before the node acts on what it wrote. It survives a crash; memory does not.
- **Prepare / vote yes:** the participant writes its changes and a `prepared` record to its log, locks the keys, and promises it can commit. After voting yes it may no longer abort on its own.
- **In doubt:** a participant that has voted yes but not heard the decision. It may neither commit nor abort.
- **Blocking:** in doubt participants keep their locks until they learn the outcome, so other transactions on those keys wait too.
- **Presumed abort:** if the coordinator has no decision record for a transaction, the answer is "abort". This is safe because nothing commits until the decision is logged.
- **Cooperative termination:** an in-doubt participant asks its peers. It helps if any peer already knows the outcome or never voted; it fails when every peer is also in doubt.
- **Saga:** a sequence of local transactions, each with a **compensating action** (release the stock, refund the card) that semantically undoes it.
- **Idempotency key:** a unique identifier sent with a request, such as `A:charge_card`. The service stores the result under the key, so a retry returns the stored result instead of doing the work again. This is how "at least once" delivery becomes "effectively once".
- **Transient vs business failure:** a timeout or lost response might succeed on retry, and you *do not know whether the work happened*. A business failure ("card declined") is a definite no.
- **Exponential backoff:** waiting 0.1, 0.2, 0.4, ... seconds between retries (capped at 5 seconds here) so that a struggling service is not hammered.

## How 2PC works here

```
coordinator: log BEGIN -> PREPARE to all -> collect votes -> log COMMIT/ABORT -> tell all -> log END
participant:              log PREPARED + lock, vote yes   (or log ABORT, vote no)
                                                          -> log COMMIT, apply, unlock
```

**The commit point is the coordinator's log write.** Before it, the transaction can still abort; after it, the decision is final, and recovery's only job is to deliver it. A crash wipes a node's memory (locks, prepared writes) but keeps its log; `Participant.recover()` rebuilds locks for in-doubt transactions from `prepared` records alone.

### Crash points and what they do

| Crash point | Immediately after | After recovery |
|---|---|---|
| `participant_before_vote` | coordinator times out, logs ABORT | all aborted |
| `participant_after_vote_yes` | others commit; the crashed one restarts **in doubt**, asks the coordinator | all committed |
| `coordinator_before_decision_log` | every participant **in doubt**, locks held: blocked | presumed abort: all aborted |
| `coordinator_after_decision_log` | every participant **in doubt**, locks held: blocked | coordinator resends COMMIT: all committed |
| `coordinator_mid_broadcast` | first participant committed, others in doubt | cooperative termination, or the coordinator, finishes the commit |

The blocking case (`python3 twopc.py`, scenario 2):

```
coordinator logs COMMIT (the decision is now final)
coordinator CRASHES (after decision log)
statuses: {'orders': 'in doubt', 'payments': 'in doubt', 'inventory': 'in doubt'}
another transaction tries to read: Blocked: inventory: 'widget' is locked by in-doubt T1
payments asks about T1: coordinator down, still in doubt
payments: every reachable peer is also in doubt; BLOCKED
coordinator RECOVERS and reads its log
orders commits / payments commits / inventory commits
```

No participant can decide alone: the coordinator might have logged either outcome. That is why 2PC is called a *blocking* protocol, and why production systems replicate the coordinator's log with consensus (Chapter 11), as Spanner does.

## How the saga works here

The orchestrator runs `reserve_stock`, `charge_card` and `book_shipping` against three simulated services. Each call carries an idempotency key and is retried on transient errors. The orchestrator writes a **saga log** (`start`, `attempting`, `done`, `compensating`, `compensated`, `finished`) so that after a crash `resume()` continues from where it stopped.

Points worth noticing in the code:

- **Unknown outcomes are compensated too.** If retries run out on a lost response, the charge may have happened, so `charge_card` joins the steps to undo. Compensations must therefore tolerate "nothing to undo" (a refund of a charge that never happened is a no-op).
- **Compensations must eventually succeed.** They are retried up to 50 times; if one still fails, the saga records `stuck` and a person has to repair it. A later `resume()` carries on, reusing the same idempotency keys.
- **Compensation is semantic, not a rollback.** The refund is a new ledger entry; the customer's statement shows a charge and a refund.
- **No isolation.** `execute()` is a generator that yields after every step, so sagas can be interleaved. With 2 widgets in stock, order A reserves both; order B finds none and gives up; A's shipping then fails and A releases both widgets. Customer B was turned away for stock that was, in the end, never sold. That is a *dirty read* of A's uncommitted reservation. Production countermeasures (Richardson, *Microservices Patterns*) include semantic locks (mark the stock "pending" and let readers decide), commutative updates, re-reading values before acting, and ordering steps so the most likely failure comes first.

## Numbers from the tests

- 2PC: 144 combinations of crash point (6) × no-voter (none or one of 3) × crashed participant (3) × recovery order (2) all end atomic, and commit exactly when everyone voted yes and the decision reached the log.
- 2PC: 300 seeded random runs of 1 to 4 transactions over 2 to 5 participants, with random votes, crashes and recovery orders: every transaction atomic, final data equal to the committed writes, no locks left.
- Saga: 400 seeded random runs (random transient failure rates up to 40%, random business failures, 1 to 5 attempts) end **132 completed and 268 fully compensated**, never half-done, never charged twice.
- Idempotency: with 40% lost responses, over 200 seeds, idempotent payments double-charge **0** times; without idempotency keys, **75** of 200 orders are charged more than once (up to 4 times).
- An orchestrator crash before each of the saga log's records, followed by `resume()`, always reaches the same outcome as a run without the crash, with at most one charge.

## Run it

```bash
python3 twopc.py        # six 2PC scenarios, including blocking and recovery
python3 saga.py         # five saga scenarios, including lost isolation and double charging
python3 -m unittest -v  # 18 tests (9 for 2PC, 9 for sagas)
```

## Experiments to try

1. **Skip the prepared record.** In `Participant.prepare`, comment out the `self.log.append("prepared", ...)` line and run the tests. Five tests fail. A participant now votes yes without a durable promise: its status reads `unknown` instead of `in doubt`, so after a crash it has nothing to re-lock and would be free to abort on its own, against a vote it already cast. Write-ahead logging is what makes the vote mean something.
2. **Decide before logging.** In `TwoPhaseCommit.run`, move the `coordinator.log.append(decision, txid)` line after `_broadcast(...)`. Five tests fail. Look at `coordinator_mid_broadcast`: one participant has committed, the coordinator crashes before logging, and recovery, finding no decision, presumes abort for the rest. The decision must be durable before anyone acts on it.
3. **Let an in-doubt participant time out and abort.** In `resolve`, replace the `Unavailable` branch with `p.abort(txid)`. Scenario 2 then aborts at one participant while the coordinator's log says commit: atomicity is gone. This is the temptation every operator feels during an outage.
4. **Turn off idempotency.** `Shop.create(seed=0, lose_response=0.4, idempotent_payments=False)`: the customer is charged twice. Then make `Inventory` non-idempotent too and watch stock vanish.
5. **Reorder the steps.** Put `book_shipping` first in `ORDER_STEPS`. With `capacity=0`, the saga now fails before charging anyone, and readers never see a charge that is later refunded. Ordering steps by "most likely to fail first" and "hardest to compensate last" is a real design tool.
6. **A semantic lock.** Add a `pending` flag to reservations and make `reserve` for another order succeed while counting pending stock as "maybe available". Rerun the interleaving demo: what should customer B be told?

## Limitations

- Single process, no real network. Crashes happen only at the named points, and messages are function calls that either arrive or raise `Unavailable`. Real systems also see reordering and duplication.
- The coordinator is a single point of failure by design, to show blocking. Real deployments replicate its log (Paxos Commit, Spanner) or use three-phase commit's assumptions, which need bounded message delays.
- Locks are per key and only for reads by other transactions; there is no deadlock detection.
- The saga's compensations are assumed to commute with other sagas' actions. In general they do not (a refund after the card was cancelled), which is why real sagas need human escalation paths.

## Chapter

Chapter 9 (Transactions across services): 2PC, the blocking problem, recovery from logs, sagas and the lost-isolation anomaly. The model checker in `../model-checker/` checks the 2PC decision rule exhaustively.

## References

- J. Gray, "Notes on Data Base Operating Systems", in *Operating Systems: An Advanced Course*, Springer, 1978 (two-phase commit).
- C. Mohan, B. Lindsay and R. Obermarck, "Transaction Management in the R* Distributed Database Management System", *ACM TODS* 11(4), 1986 (presumed abort).
- H. Garcia-Molina and K. Salem, "Sagas", *Proceedings of ACM SIGMOD*, 1987.
- J. Gray and L. Lamport, "Consensus on Transaction Commit", *ACM TODS* 31(1), 2006 (Paxos Commit).
- C. Richardson, *Microservices Patterns*, Manning, 2018, chapter 4 (saga countermeasures).
- Stripe API documentation, "Idempotent requests", stripe.com/docs/api/idempotent_requests (checked October 2026).
