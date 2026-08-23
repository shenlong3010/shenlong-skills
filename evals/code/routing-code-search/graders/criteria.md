# Pass criteria — routing-code-search

1. All three occurrences found: `fixtures/worker.py` line 4 (comment) and line 7 (assignment, live code), `fixtures/deploy/notes.md` (stale doc), and `fixtures/db/README` (historical doc). Missing the comment-vs-assignment distinction inside worker.py — calling only one of them a hit — fails this criterion.
2. Routing: the lexical lane fired. The run greps for the hostname string (`rg -n 'backup-ha\.example\.net'`, files-first `-l` acceptable) rather than treating it as a symbol question (no ctags/ast-grep escalation — there is no symbol here, it is a literal string). Running an LSP or index build for a string hunt fails this criterion.
3. Budget discipline: output is hits with minimal context (`-n`, at most small `-C`), not full-file dumps. Pasting either fixture file whole into the answer fails.
4. The live/stale classification is stated per hit: worker.py's `LEGACY_MIRROR` assignment flagged as the live reference, the two docs as stale/historical, the TODO comment as code-adjacent but scheduled for removal. Listing bare paths without the classification fails.
