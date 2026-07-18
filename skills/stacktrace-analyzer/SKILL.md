---
name: stacktrace-analyzer
description: Analyze a stack trace or exception dump into ranked root-cause hypotheses with concrete next checks. Use whenever a trace, exception, panic, or crash log is pasted or found in logs — "what does this error mean", "why is this throwing", "analyze this trace".
derivation: original
flow: debug
domain: code
---

# Stacktrace Analyzer

## Method
1. **Locate the boundary.** Find the deepest frame in *the user's own code* — frames inside frameworks/JDK/stdlib are usually consequences, not causes. The user-code frame adjacent to the library boundary is the prime suspect.
2. **Read the exception chain bottom-up.** `Caused by` chains: the last cause is the origin; everything above is wrapping. Report the origin first.
3. **Classify** the failure: null/absent value, type/serialization mismatch, resource exhaustion (pool, memory, fd), concurrency (deadlock, CME, race), configuration/environment, or genuine logic error. The class determines the next check.
4. **Hypotheses, ranked** — at most 3, each with: what would have to be true, and the single cheapest check that confirms or kills it (a log line to add, a value to print, a config to cat, a test to run).
5. **Ask for the one missing input** only if the trace genuinely underdetermines the cause (e.g., need the request payload or the config in effect) — name exactly what and why.

## Rules
Never present one hypothesis as fact when the trace supports several. Line numbers may be stale against the working tree — check file versions before trusting them. Async/reactive traces: the scheduler frames hide the submission site; look for framework-provided assembly/cause markers before concluding.
