# Pass criteria — routing-log-triage

1. Correct root cause: the run identifies the DB connection-pool exhaustion on the orders service (`db pool exhausted`, pool `orders`, 0/20 free) around 10:17 as the real incident — the FATAL/ERROR burst, not the chronic cache-miss WARNs.
2. Routing: the `log-triage` skill lane fired — the log is normalized/clustered so volume is separated from importance, rather than read top-to-bottom or summarized by frequency. Concluding that the cache-miss WARNs are the problem *because there are ~120 of them* fails this criterion — that is the "volume ≠ importance" trap the skill exists to avoid. The 4-line FATAL cluster (rare) is what matters over the 120 WARNs (common).
3. Timeline: the run places the incident in its narrow window (~10:17) and distinguishes it from the steady-state noise spanning the whole file, rather than treating all 143 lines as one undifferentiated event.

Note: the fixture is 143 lines with the anomaly (4 lines) buried in ~120 chronic WARNs — large enough that reading it all and ranking by frequency is observably the wrong move.
