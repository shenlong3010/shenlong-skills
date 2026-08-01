# Pass criteria — routing-diff-read

1. Correct finding: the run identifies the boundary change in `src/auth/session.js` — `isExpired` changed from `session.expiresAt < now` to `session.expiresAt <= now` — as the one behavioral change in the diff. Reporting only "it's a `legacyClient` → `apiClient` rename" fails this criterion; that is the answer the diff's bulk suggests and the reason this case exists.

2. Routing: the `diff-read` lane fired — the diff is approached stat-first (`--stat`/`--numstat`, or per-file inspection driven by that overview) so the 10-file shape is established before any hunk is read. Paging all 817 lines into context to answer a question about *whether* behavior changed fails this criterion even if the `<=` is found.

   The stat is the whole shortcut here: nine handler files report exactly `28` changed lines each and `src/auth/session.js` reports `4`. The outlier is visible before a single hunk is read, and a stat-first run should reach `session.js` *because* it is the file that does not match the pattern — not by scanning until it happens to notice a `<=`. A run that finds the right answer by reading every hunk in order has failed the routing criterion while passing criterion 1.

3. The two change classes are distinguished: the mechanical rename (9 files, `legacyClient` → `apiClient`, no behavior change) is separated from the semantic one (1 file, boundary condition). A run that lists `src/auth/session.js` among the renamed files without noting it also carries a logic change fails — `session.js` contains *both* kinds of edit, and collapsing them is the specific error the separation is meant to catch.

4. The behavioral consequence is stated, not just the syntax: `<=` means a session whose `expiresAt` is exactly `now` is now treated as expired (an off-by-one at the boundary, flipping one instant's worth of sessions from valid to invalid). Naming the character change without saying what it does to a request fails this criterion.

Note: the fixture is a real `git diff` (validated with `git apply --check` against a clean tree — 10 files, 128 insertions, 128 deletions). The rename touches 9 handler files uniformly at 28 lines each; `src/auth/session.js` is the only file where an insertion is not a pure rename, and the only one whose stat line differs. Two consequences for grading: a run that never looks at the stat has to read ~817 lines to find what the stat surfaces in one, and a run that reads only the stat still has to open `session.js` to say *what* changed — the stat localizes the anomaly, it does not explain it.
