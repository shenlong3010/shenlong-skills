---
name: flaky-suite-triage
description: Diagnose test suites that pass alone but fail together, pass locally but fail CI, or fail intermittently across runs — ordering dependence, shared state, parallel-worker collisions, and resource leaks at the suite level. Use for "tests pass individually but not in the suite", "flaky CI", "test order matters", "fails only with -n 4", "random suite failures". Do NOT use for a single test failing deterministically or one intermittently-failing bug — that is `systematic-debug`; this skill owns the *interactions between tests*.
derivation: original
flow: debug
domain: process
---

# Flaky Suite Triage

A flaky test is a bug you've agreed to ignore on a schedule. Suite-level flake has distinct mechanics from single-test bugs — the failure lives in *shared state between tests*, so the unit of investigation is pairs and orderings, not the failing assertion.

## Method

1. **Quantify before diagnosing.** Re-run to get a rate (10 runs → fails k/N). A 1/20 flake and an 8/20 flake are different investigations. Capture the exact invocation that fails — seed, worker count, order file (`pytest -p randomly --seed <s>`; record it).
2. **Bisect the interaction.** Fails-in-suite-passes-alone is ordering: reproduce with the recorded seed, then halve the candidate set (run the failing test against successively smaller prefixes of the suite order) until the polluter pair is isolated. Tools that do this mechanically exist (`pytest-find-polluter`-class); manual prefix-bisection converges in ~log₂(n) runs regardless.
3. **Sweep the shared-state suspects** once a polluter exists: module globals and class attributes mutated in tests; monkeypatches without undo; cwd/env-var changes; files written outside `tmp_path` fixtures; DB rows surviving across tests (missing transaction rollback); free ports grabbed without release; sockets/tempfiles left open (Windows: open handles also block cleanup — a "passing" run can still leak).
4. **Classify CI-only flakes as resource ceilings.** Same suite green locally, red in CI usually means parallelism pressure: worker count vs CPU, per-worker timeouts under load, container memory. Drop workers (`-n 2`, `--runInBand`) to confirm before touching test code.
5. **Fix at the seam, not the symptom.** The right fix makes state isolation structural (function-scoped fixtures, factory teardown, port allocation helper), not a bigger sleep or another retry. Sleep-based waits relocate races to slower machines.
6. **Quarantine is a tracked debt, not a fix.** If a fix can't land now: mark it (`@pytest.mark.flaky(reruns=N)` / xfail with reason+ticket link), and give it an expiry — a quarantine older than a sprint is a standing hole in the regression net.

## Gotchas

- **Retries convert detectors into amplifiers.** Rerun-until-green hides exactly the class of bug flakes advertise. Retries are a *metric* (log every rerun) — never a default config.
- **The innocent-recent-change trap:** bisecting commits for a flake implicates whoever touched nearby code last, when the real cause predates them. Confirm the mechanism (step 3) before accepting a commit-range verdict.
- **Order-dependence has two directions:** the polluter breaks the victim, but fixing the victim's assumptions often fixes the whole class — victims should assert on clean state, not on whatever the previous test left.
- **Verify plugin flags against installed versions** (pytest-randomly, xdist move); examples here were written against pytest-7-era flags. Windows lane: all commands are PowerShell-native via `pytest`; no POSIX-only tooling in this skill.

## Boundaries

- One test, deterministic red (or intermittent because of a genuine race *inside* one code path) → `systematic-debug`.
- Writing the missing regression test after diagnosis → `tdd-loop`; whether that new test means anything → `test-reviewer`.
- CI log dump full of unrelated noise first → `log-triage` to find the signal worth triaging here.
