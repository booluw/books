"""Swarm runner: search seeds for a broken invariant, then replay the failure.

Usage:
    python3 swarm.py                 # search 10,000 seeds, replay the first failure, check the fix
    python3 swarm.py --seeds 2000    # search fewer seeds
    python3 swarm.py --seed 100      # print the full trace of one seed (buggy version)
    python3 swarm.py --seed 100 --fixed
"""

from __future__ import annotations

import argparse
import re
import time

from primary_backup import RunResult, run


def swarm(seeds: range, buggy: bool = True) -> tuple[list[int], float]:
    """Run every seed; return the failing seeds and the elapsed seconds."""
    start = time.perf_counter()
    failures = [s for s in seeds if not run(s, buggy=buggy).ok]
    return failures, time.perf_counter() - start


def story(result: RunResult) -> list[str]:
    """The trace lines that explain a lost write: messages and log lines that
    mention a lost op, plus the crash, the failover and the final check."""
    ops = {op for op, _ in result.lost}
    mentions = [rf"[\s\[(]{op}[,\])]" for op in ops]     # " 7," " 7)" "[7]" " 7]"
    pattern = re.compile("|".join(mentions + ["CRASH", "FAILOVER", "END"]))
    return [line for line in result.trace if pattern.search(line)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=10_000)
    parser.add_argument("--seed", type=int, help="print the full trace of one seed")
    parser.add_argument("--fixed", action="store_true", help="use the corrected primary")
    args = parser.parse_args()

    if args.seed is not None:
        r = run(args.seed, buggy=not args.fixed, trace=True)
        print("\n".join(r.trace))
        print(f"\nconfig: {r.config}\ninvariant {'holds' if r.ok else 'VIOLATED'}; "
              f"trace hash {r.trace_hash}")
        return

    seeds = range(args.seeds)
    failures, elapsed = swarm(seeds, buggy=True)
    print(f"Buggy primary: {len(seeds):,} seeds in {elapsed:.1f} s "
          f"({elapsed / len(seeds) * 1e3:.2f} ms per run)")
    print(f"Invariant 'no acknowledged write is lost' violated in {len(failures)} seeds "
          f"({len(failures) / len(seeds):.2%})")
    if not failures:
        return
    print(f"First failing seeds: {failures[:10]}\n")

    first = failures[0]
    replays = [run(first, buggy=True, trace=True) for _ in range(3)]
    print(f"Replaying seed {first} three times:")
    print(f"{'replay':>7}{'trace events':>14}{'trace hash':>18}{'acked':>7}  lost (op, counter)")
    for i, r in enumerate(replays, 1):
        print(f"{i:>7}{len(r.trace):>14}{r.trace_hash:>18}{r.acked:>7}  {r.lost}")
    r = replays[0]
    print(f"\nSeed {first} configuration: {r.config}\n")
    print("What happened (trace lines that mention the lost op, plus crash and failover):")
    for line in story(r):
        print("  " + line)

    fixed_failures, elapsed = swarm(seeds, buggy=False)
    print(f"\nFixed primary (acks matched by op id): {len(seeds):,} seeds in {elapsed:.1f} s, "
          f"{len(fixed_failures)} violations")
    fixed = run(first, buggy=False, trace=True)
    print(f"Seed {first} with the fix: acked {fixed.acked}, lost {fixed.lost}, "
          f"trace hash {fixed.trace_hash}")


if __name__ == "__main__":
    main()
