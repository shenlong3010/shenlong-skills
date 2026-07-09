#!/usr/bin/env python3
"""Run a command N times; classify PASS / FAIL / FLAKY.
Usage: flaky-detector.py -n 5 -- <command...>
FLAKY = mixed exit codes across runs; treat flaky evals as triage items, not regressions."""
import subprocess, sys

def main() -> int:
    args = sys.argv[1:]
    n = 5
    if args[:1] == ["-n"]:
        n = int(args[1]); args = args[2:]
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        print(__doc__); return 2
    codes = []
    for i in range(n):
        r = subprocess.run(args, capture_output=True)
        codes.append(r.returncode)
        print(f"run {i+1}/{n}: exit {r.returncode}")
    if all(c == 0 for c in codes):
        print("verdict: PASS"); return 0
    if all(c != 0 for c in codes):
        print("verdict: FAIL (deterministic)"); return 1
    rate = codes.count(0) / n
    print(f"verdict: FLAKY (pass rate {rate:.0%}) — fix the test or quarantine; do not gate on it")
    return 3

if __name__ == "__main__":
    sys.exit(main())
