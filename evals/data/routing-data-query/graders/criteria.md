# Pass criteria — routing-data-query

1. Correct value reported: `3`, at path `services.worker.limits.retry_budget`.
2. Routing: the JSON is queried structurally — `jq`, `gron`, or any real parser (stdlib `json` path-walk counts) — not `grep`/`rg` against the minified text. Text-grep on a one-line minified file fails this criterion even if the value is found; which structured tool is used does not matter.
3. The reported path is the object path, not a byte offset or line number (the file is one line — line numbers are meaningless, and saying so is acceptable).
