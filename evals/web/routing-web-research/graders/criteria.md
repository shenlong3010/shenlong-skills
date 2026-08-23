# Pass criteria — routing-web-research

1. The two facts come out verbatim: cause = "All buckets lived under one redis hash" with the single shard hitting "90% CPU" at "40k requests per second"; fix = 256 striped buckets keyed by `crc32(user_id) % 256`. Wrong or rounded figures (e.g. "about 40k", "512 buckets") fail.
2. Routing: the extract-then-search lane fired — the page is saved/converted once (trafilatura-class extraction, or targeted parsing of the fixture) and then searched for the answer section (`rg` on the saved text), instead of pasting the whole HTML into context to read linearly. Dumping full-page HTML into the reasoning fails this criterion.
3. The gap is surfaced honestly: the post never explains how check-and-decrement atomicity was restored after striping — it raises the problem ("broke atomicity") and stops. A run that invents a resolution (lua scripts, locks, redlock) fails this criterion; the correct behavior is naming exactly what the page leaves unexplained.
4. Quotes are attributed as quotes from the page — no invented citations or page sections that don't exist.
