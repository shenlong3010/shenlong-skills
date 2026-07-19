# Pass criteria — routing-data-query

1. Correct value reported: `3`, at path `services.worker.limits.retry_budget`.
2. Routing: a structured query tool is used — `jq` (e.g. `jq 'paths(..)'`-style or direct path query) or `gron` — not `grep`/`rg` against the minified JSON. Grep on a one-line minified file fails this criterion even if the value is found.
3. The reported path is the object path, not a byte offset or line number (the file is one line — line numbers are meaningless, and saying so is acceptable).
