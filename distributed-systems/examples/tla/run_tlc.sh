#!/usr/bin/env bash
# run_tlc.sh: model-check every spec in this folder with TLC and report results.
#
# Usage:
#   TLA2TOOLS=/path/to/tla2tools.jar ./run_tlc.sh        # all specs
#   ./run_tlc.sh RaftElection                             # only configs of one spec
#
# Environment variables:
#   TLA2TOOLS  path to tla2tools.jar (default: ./tla2tools.jar)
#   WORKERS    TLC worker threads (default: 1, which makes BFS deterministic
#              and guarantees the shortest counterexample; use "auto" for speed)
#   KEEP=1     keep the temporary working directory (with full TLC logs)
#
# TLC writes a states/ directory and trace files next to the spec it checks.
# To keep the repository clean, this script copies the specs into a fresh
# temporary directory and runs TLC there.
#
# Some configurations are EXPECTED to fail: they exist to show the
# counterexample TLC prints.  Those are reported as "expected violation found".
# The script exits non-zero only if a result differs from the expectation.
set -u

here="$(cd "$(dirname "$0")" && pwd)"
jar="${TLA2TOOLS:-./tla2tools.jar}"
case "$jar" in /*) ;; *) jar="$PWD/$jar" ;; esac
workers="${WORKERS:-1}"
filter="${1:-}"

if [ ! -f "$jar" ]; then
  echo "tla2tools.jar not found at $jar"
  echo "Download it from https://github.com/tlaplus/tlaplus/releases and set TLA2TOOLS."
  exit 2
fi
command -v java >/dev/null || { echo "java not found on PATH (TLC needs Java 11+)"; exit 2; }

work="$(mktemp -d "${TMPDIR:-/tmp}/tlc-run.XXXXXX")"
if [ "${KEEP:-0}" = "1" ]; then
  echo "Working directory (kept): $work"
else
  trap 'rm -rf "$work"' EXIT
fi
cp "$here"/*.tla "$here"/*.cfg "$work"/

# spec | config | expected outcome ("pass" or "violation")
cases="
DieHard|DieHard.cfg|violation
TwoPhaseCommit|TwoPhaseCommit.cfg|pass
QuorumIntersection|QuorumIntersection.cfg|pass
QuorumIntersection|QuorumIntersection_bad.cfg|violation
LockWithFencing|LockWithFencing.cfg|pass
LockWithFencing|LockWithFencing_bad.cfg|violation
RaftElection|RaftElection.cfg|pass
RaftElection|RaftElection_bad.cfg|violation
RaftElection|RaftElection_forgetvote_bad.cfg|violation
"

unexpected=0
printf '%-20s %-34s %-30s %s\n' "SPEC" "CONFIG" "RESULT" "DETAILS"
for line in $cases; do
  IFS='|' read -r spec cfg expect <<<"$line"
  if [ -n "$filter" ] && [ "$spec" != "$filter" ]; then continue; fi
  log="$work/${cfg%.cfg}.log"
  ( cd "$work" && java -XX:+UseParallelGC -cp "$jar" tlc2.TLC \
      -workers "$workers" -deadlock -metadir "$work/states/${cfg%.cfg}" \
      -config "$cfg" "$spec.tla" ) >"$log" 2>&1

  # TLC's summary line: "N states generated, M distinct states found, K states left on queue."
  nums=($(grep -E 'states generated, .* distinct states found' "$log" | tail -1 | grep -oE '[0-9]+'))
  depth="$(grep -E 'depth of the complete state graph' "$log" | grep -oE '[0-9]+' | tail -1)"
  secs="$(grep -E '^Finished in' "$log" | tail -1 | sed -E 's/^Finished in ([^ ]+) .*/\1/')"
  details="generated ${nums[0]:-?}, distinct ${nums[1]:-?}, depth ${depth:-?}, time ${secs:-?}"

  if grep -q 'Model checking completed. No error has been found.' "$log"; then
    actual=pass
  elif grep -qE 'Error: (Invariant .* is violated|Temporal properties were violated)' "$log"; then
    actual=violation
    details="$(grep -E '^Error: (Invariant|Temporal)' "$log" | head -1 | sed 's/^Error: //; s/\.$//'); $details"
  else
    actual=error
  fi

  if [ "$actual" = "$expect" ]; then
    if [ "$actual" = pass ]; then result="PASS"; else result="expected violation found"; fi
  else
    result="UNEXPECTED ($actual, wanted $expect)"
    unexpected=$((unexpected + 1))
  fi
  printf '%-20s %-34s %-30s %s\n' "$spec" "$cfg" "$result" "$details"
  if [ "$actual" = error ]; then sed 's/^/    | /' "$log" | tail -20; fi
done

echo
if [ "$unexpected" -eq 0 ]; then
  echo "All results match expectations."
else
  echo "$unexpected result(s) did not match expectations."
fi
exit $(( unexpected > 0 ))
