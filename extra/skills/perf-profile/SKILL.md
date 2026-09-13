---
name: perf-profile
description: Measure before theorizing when something is slow — sampling profilers, flamegraph reading, and the fix-verification loop for app-level performance work. Use for "why is this slow", "it got slower after X", "CPU is pegged", "latency doubled", "profile this endpoint" — whenever a guess about the cause is forming without a measurement behind it. Do NOT use for a single slow SQL statement (`sql-review`), correctness bugs that merely manifest as slowness (`systematic-debug`), or which process eats CPU right now (`system-lookup`).
derivation: original
flow: debug
domain: system
---

# Perf Profile

Slowness is a measurement problem before it is a code problem. Every optimization made without a profile is a bet placed with house money — and most such bets lose to a config default, an N+1, or an accidental O(n²) on real data volume.

## Method

1. **Define the question in numbers.** Which operation, measured how (p50 vs p99, wall vs CPU), from what baseline? "Faster" is not a goal; "checkout p95 under 400 ms at 50 rps" is. If no load reproduces it, build the smallest harness that does — a slow-only-in-prod problem needs prod-shaped data volume, because linear-looking code hides its quadratic term until n is real.
2. **Measure the baseline and keep the script.** The benchmark that demonstrated the problem is also the one that proves the fix. Commit it next to the change (repo rule 5: machine-verifiable done). Re-measure after every single change — two optimizations landing together means neither has evidence.
3. **Sample first, instrument second (Python lane).** `py-spy top --pid <pid>` answers "where are we right now" with near-zero distortion; `py-spy record -o profile.svg --pid <pid>` (or `--format speedscope`) gives the flamegraph. Only drop to `cProfile`/`pyinstrument` when you need *call counts*, not just time shares — cProfile instruments every call and distorts exactly the hot loops you're hunting.
4. **Read the flamegraph by width.** Width = share of sampled stack time; plateaus you own are candidates; plateaus in libraries/frameworks are context, not targets. A frame missing from the graph usually means native/inlined code or I/O wait, not "nothing happened".
5. **Distinguish CPU-bound from wait-bound.** A CPU profiler shows nothing meaningful for code blocked on network/disk/locks — if samples show idle-ish stacks while latency is high, measure the waits (connection-pool exhaustion, upstream latency, lock contention), don't optimize the CPU path.
6. **Close the loop.** Fix lands → same benchmark, same data, before/after numbers in the PR. No improvement measurable at the stated question = revert, however elegant.

## Gotchas

- **Observer effect is asymmetric:** sampling profilers distort little; instrumenting ones rewrite your hot-path economics. Profile with the tool whose bias you can afford.
- **Async code lies to cProfile:** interleaved coroutines attribute time to the event loop, not the awaiting task. Sample with py-spy instead, and read task-level timing from the framework (or instrument per-await explicitly) before blaming the loop.
- **Warmup and caches:** first-request timings include imports, JITs, connection pools, and cold caches. Warm up before measuring, or you'll "optimize" initialization and call it throughput.
- **p99 ≠ mean:** tail latency lives in GC pauses, lock convoys, and retry storms that averages hide. If the complaint is "sometimes slow", profile the tail — capture during the spike (`py-spy dump` repeatedly), not after it.
- **Verify flags against the installed version** — profiler CLIs move (`pip show py-spy`; `py-spy record --help`), and this skill's examples were written against py-spy 0.3.x-era flags. Windows note: py-spy ships Windows wheels and works against live processes; run the shell commands from PowerShell directly, no Git Bash needed.

## Boundaries

- One SQL statement's plan/indexes → `sql-review`. App-level slowness *caused* by queries still starts here — bring the profile, let sql-review own the statement.
- The mechanism behind intermittent slowness (race, retry storm, cache stampede) → `systematic-debug` once profiling has localized it.
- Port/process/file-handle questions ("what is pegging the box") → `system-lookup`.
