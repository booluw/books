"""A saga orchestrator for an order workflow (Chapter 9).

Two-phase commit needs every service to hold locks while a coordinator
decides, and blocks if the coordinator disappears. Across independently
owned services (an inventory system, a payment provider, a courier's API)
that is rarely acceptable, and often impossible: the card network will not
"prepare" a charge for you.

A **saga** (Garcia-Molina and Salem, 1987) instead runs a sequence of local
transactions, each committed immediately. If a later step fails, the saga
runs **compensating actions** for the steps already done, in reverse order:
release the stock, refund the card. The result is atomic in the end (all
done, or all undone) but **not isolated**: other readers can see the
intermediate states, such as reserved stock for an order that is about to
be cancelled.

The orchestrator here:

* gives every call an **idempotency key** (``order-id:step`` or
  ``order-id:step:undo``) so a retried call is applied at most once;
* **retries** transient failures (a timeout, a lost response) with
  exponential backoff, and treats business failures (card declined) as
  final;
* writes a durable **saga log** so a crashed orchestrator can ``resume``;
* is a generator that yields after every step, so two sagas can be
  interleaved to show what concurrent readers see.

Run ``python3 saga.py`` for the walk-through.
"""

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional, Tuple


class TransientError(Exception):
    """Timeout or lost response: the call may or may not have happened."""


class BusinessError(Exception):
    """A definite "no" (out of stock, card declined). Retrying will not help."""


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

class Service:
    """Base class: simulated network failures and idempotency keys.

    ``fail_before`` is the chance a request is lost before it is processed;
    ``lose_response`` the chance the work is done but the reply is lost.
    The second case is the dangerous one: the caller sees a timeout and
    cannot tell whether the work happened.
    """

    def __init__(self, name: str, rng: random.Random, fail_before: float = 0.0,
                 lose_response: float = 0.0, idempotent: bool = True) -> None:
        self.name = name
        self.rng = rng
        self.fail_before = fail_before
        self.lose_response = lose_response
        self.idempotent = idempotent
        self.results: Dict[str, object] = {}   # idempotency key -> stored outcome
        self.calls = 0

    def call(self, key: str, operation: Callable[[], object]) -> object:
        self.calls += 1
        if self.rng.random() < self.fail_before:
            raise TransientError(f"{self.name}: request timed out")
        if self.idempotent and key in self.results:
            outcome = self.results[key]               # replay: do not repeat the work
        else:
            try:
                outcome = operation()
            except BusinessError as e:
                outcome = e
            self.results[key] = outcome
        if self.rng.random() < self.lose_response:
            raise TransientError(f"{self.name}: response lost")
        if isinstance(outcome, BusinessError):
            raise outcome
        return outcome


class Inventory(Service):
    def __init__(self, rng, stock: Dict[str, int], **kw) -> None:
        super().__init__("inventory", rng, **kw)
        self.stock = dict(stock)
        self.reservations: Dict[str, Tuple[str, int]] = {}   # order -> (sku, qty)

    def reserve(self, key: str, order: str, sku: str, qty: int):
        def op():
            if order in self.reservations:
                return "already reserved"
            if self.stock.get(sku, 0) < qty:
                raise BusinessError(f"out of stock: {sku}")
            self.stock[sku] -= qty
            self.reservations[order] = (sku, qty)
            return "reserved"
        return self.call(key, op)

    def release(self, key: str, order: str):
        def op():
            if order not in self.reservations:
                return "nothing to release"          # compensations must tolerate this
            sku, qty = self.reservations.pop(order)
            self.stock[sku] += qty
            return "released"
        return self.call(key, op)


class Payments(Service):
    def __init__(self, rng, card_limit: int = 1000, **kw) -> None:
        super().__init__("payments", rng, **kw)
        self.card_limit = card_limit
        self.ledger: List[Tuple[str, str, int]] = []         # (order, "charge"/"refund", amount)

    def net_charged(self, order: str) -> int:
        return sum(a if kind == "charge" else -a for o, kind, a in self.ledger if o == order)

    def charges(self, order: str) -> int:
        return sum(1 for o, kind, _ in self.ledger if o == order and kind == "charge")

    def charge(self, key: str, order: str, amount: int):
        def op():
            if amount > self.card_limit:
                raise BusinessError("card declined")
            self.ledger.append((order, "charge", amount))
            return f"charged {amount}"
        return self.call(key, op)

    def refund(self, key: str, order: str):
        def op():
            owed = self.net_charged(order)
            if owed <= 0:
                return "nothing to refund"
            self.ledger.append((order, "refund", owed))
            return f"refunded {owed}"
        return self.call(key, op)


class Shipping(Service):
    def __init__(self, rng, capacity: int = 10, **kw) -> None:
        super().__init__("shipping", rng, **kw)
        self.capacity = capacity
        self.bookings: Dict[str, str] = {}

    def book(self, key: str, order: str, address: str):
        def op():
            if order in self.bookings:
                return "already booked"
            if len(self.bookings) >= self.capacity:
                raise BusinessError("no courier capacity")
            self.bookings[order] = address
            return "booked"
        return self.call(key, op)

    def cancel(self, key: str, order: str):
        def op():
            return "cancelled" if self.bookings.pop(order, None) else "nothing to cancel"
        return self.call(key, op)


@dataclass
class Shop:
    inventory: Inventory
    payments: Payments
    shipping: Shipping

    @classmethod
    def create(cls, seed: int = 0, stock=None, card_limit=1000, capacity=10,
               fail_before=0.0, lose_response=0.0, idempotent_payments=True) -> "Shop":
        rng = random.Random(seed)
        kw = dict(fail_before=fail_before, lose_response=lose_response)
        return cls(Inventory(rng, stock or {"widget": 5}, **kw),
                   Payments(rng, card_limit, idempotent=idempotent_payments, **kw),
                   Shipping(rng, capacity, **kw))

    def snapshot(self) -> str:
        return (f"stock={self.inventory.stock} reserved={sorted(self.inventory.reservations)} "
                f"charged={ {o: self.payments.net_charged(o) for o, _, _ in self.payments.ledger} } "
                f"shipments={sorted(self.shipping.bookings)}")


# ---------------------------------------------------------------------------
# The orchestrator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Order:
    id: str
    sku: str
    qty: int
    amount: int
    address: str = "1 High Street"


@dataclass
class Step:
    name: str
    action: Callable[[Shop, str, Order], object]
    compensation: Callable[[Shop, str, Order], object]


ORDER_STEPS = [
    Step("reserve_stock",
         lambda shop, key, o: shop.inventory.reserve(key, o.id, o.sku, o.qty),
         lambda shop, key, o: shop.inventory.release(key, o.id)),
    Step("charge_card",
         lambda shop, key, o: shop.payments.charge(key, o.id, o.amount),
         lambda shop, key, o: shop.payments.refund(key, o.id)),
    Step("book_shipping",
         lambda shop, key, o: shop.shipping.book(key, o.id, o.address),
         lambda shop, key, o: shop.shipping.cancel(key, o.id)),
]


class OrchestratorCrash(Exception):
    pass


@dataclass
class Saga:
    """One order's saga. ``log`` is the durable saga log."""

    shop: Shop
    order: Order
    steps: List[Step] = field(default_factory=lambda: list(ORDER_STEPS))
    max_attempts: int = 4
    compensation_attempts: int = 50
    log: List[tuple] = field(default_factory=list)
    trace: List[str] = field(default_factory=list)
    backoff_waited: float = 0.0
    crash_before_record: Optional[int] = None
    """Testing hook: simulate an orchestrator crash just before the saga log
    reaches this many records (the work before it is done, but not logged)."""

    @property
    def outcome(self) -> Optional[str]:
        for record in self.log:
            if record[0] == "finished":
                return record[1]
        return None

    def _log(self, *record) -> None:
        if self.crash_before_record is not None and len(self.log) + 1 >= self.crash_before_record:
            self.crash_before_record = None
            raise OrchestratorCrash(f"orchestrator crashed before logging {record}")
        self.log.append(record)

    def _call(self, fn, key: str, attempts: int) -> Tuple[str, object]:
        """Call with retries. Returns ("ok", result), ("business", error) or
        ("unknown", error) when retries ran out on transient errors."""
        delay, last_error = 0.1, None
        for attempt in range(1, attempts + 1):
            try:
                return "ok", fn(self.shop, key, self.order)
            except BusinessError as e:
                return "business", e
            except TransientError as e:
                last_error = e
                self.trace.append(f"{key}: attempt {attempt} failed ({e})")
                if attempt < attempts:
                    self.backoff_waited += delay
                    delay = min(delay * 2, 5.0)      # exponential backoff, capped
        return "unknown", last_error

    def run(self) -> str:
        for _ in self.execute():
            pass
        return self.outcome

    def execute(self) -> Iterator[str]:
        """Run (or resume) the saga, yielding a description after each step."""
        records = [r[0] for r in self.log]
        if "finished" in records:
            return
        if "start" not in records:
            self._log("start", self.order.id)
        done = [r[1] for r in self.log if r[0] == "done"]
        if "compensating" not in records:
            for step in self.steps:
                if step.name in done:
                    continue                          # resumed: already completed
                key = f"{self.order.id}:{step.name}"
                self._log("attempting", step.name)
                status, result = self._call(step.action, key, self.max_attempts)
                if status == "ok":
                    self._log("done", step.name)
                    done.append(step.name)
                    yield f"{step.name}: {result}"
                    continue
                # Failed. If the outcome is unknown, the step may have happened,
                # so it must be compensated too.
                to_undo = done + ([step.name] if status == "unknown" else [])
                self._log("compensating", tuple(to_undo), str(result))
                yield f"{step.name}: FAILED ({result}); compensating {to_undo}"
                break
            else:
                self._log("finished", "completed")
                yield "saga completed"
                return
        yield from self._compensate()

    def _compensate(self) -> Iterator[str]:
        to_undo = next(r[1] for r in self.log if r[0] == "compensating")
        undone = {r[1] for r in self.log if r[0] == "compensated"}
        by_name = {s.name: s for s in self.steps}
        for name in reversed(to_undo):
            if name in undone:
                continue
            key = f"{self.order.id}:{name}:undo"
            status, result = self._call(by_name[name].compensation, key,
                                        self.compensation_attempts)
            if status != "ok":
                # A compensation must eventually succeed; if it cannot, a person must act.
                self._log("stuck", name)
                yield f"undo {name}: STUCK ({result}); needs manual repair"
                return
            self._log("compensated", name)
            yield f"undo {name}: {result}"
        self._log("finished", "compensated")
        yield "saga compensated"

    def resume(self) -> str:
        """Continue after an orchestrator crash, from the saga log alone."""
        self.trace.append("orchestrator restarts and replays the saga log")
        return self.run()


def demo() -> None:
    print("== 1. Happy path")
    shop = Shop.create()
    saga = Saga(shop, Order("A", "widget", 2, 40))
    for line in saga.execute():
        print(f"  {line}\n      {shop.snapshot()}")

    print("\n== 2. Shipping has no capacity: compensate in reverse order")
    shop = Shop.create(capacity=0)
    saga = Saga(shop, Order("A", "widget", 2, 40))
    for line in saga.execute():
        print(f"  {line}\n      {shop.snapshot()}")

    print("\n== 3. Lack of isolation: two interleaved orders, 2 widgets in stock")
    shop = Shop.create(stock={"widget": 2}, capacity=0)
    a = Saga(shop, Order("A", "widget", 2, 40)).execute()
    b = Saga(shop, Order("B", "widget", 1, 20)).execute()
    print(f"  A {next(a)}")
    print(f"  B {next(b)}    <- B sees A's uncommitted reservation")
    for line in a:
        print(f"  A {line}")
    for line in b:
        print(f"  B {line}")
    print(f"  final: {shop.snapshot()}")
    print("  Customer B was turned away for stock that A then released.")

    print("\n== 4. Lost responses: retries with idempotency keys")
    for idempotent in (True, False):
        shop = Shop.create(seed=0, lose_response=0.4, idempotent_payments=idempotent)
        saga = Saga(shop, Order("A", "widget", 1, 25))
        outcome = saga.run()
        print(f"  idempotent={idempotent!s:<5} outcome={outcome:<11} "
              f"charges={shop.payments.charges('A')} net={shop.payments.net_charged('A')} "
              f"payment calls={shop.payments.calls}")

    print("\n== 5. Orchestrator crashes after charging, before logging it; resumes")
    shop = Shop.create()
    saga = Saga(shop, Order("A", "widget", 1, 25), crash_before_record=5)
    try:
        saga.run()
    except OrchestratorCrash as e:
        print(f"  {e}")
        print(f"  log so far: {[r[0] + ':' + str(r[1]) for r in saga.log]}")
    print(f"  resume -> {saga.resume()}; charges={shop.payments.charges('A')}; "
          f"{shop.snapshot()}")


if __name__ == "__main__":
    demo()
