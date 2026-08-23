# Pass criteria — routing-file-find

1. Biggest file named correctly: `fixtures/.cache/tiles.dat` at ~40 KB (40,000 bytes). Reporting `worker.log` fails — it is second (~18 KB); the largest sits in a hidden directory, so a listing that skips hidden entries misses it.
2. Both backup files found: `logs/worker.log.bak` and `.cache/tiles.dat~`. Either one missing fails; the `~` file is deliberately in the hidden `.cache/` directory.
3. Routing: a filename/size lane fired — `fd` with size/pattern flags (`fd -S +10k`, `fd -H '(\.bak|~)$'`) or an equivalent `find` invocation. Reading every file's contents to answer "which is biggest" fails this criterion; this is a name/metadata question, not a content search.
4. Hidden-dir handling is explicit: the run either includes hidden entries (`fd -H` / `find` default) or states that it did not and what that would miss. Silently skipping `.cache/` while reporting a confident answer fails.
5. Output stays names + sizes — no file contents echoed into the answer.
