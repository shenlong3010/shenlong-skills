# Pass criteria — talk-notes-jargon-catch

Ground truth: `fixtures/manual-transcript.txt` is the video's real (manual-caption) transcript. The MCP transcript tool for this video returns an **auto-caption** track that garbles five specific terms. A run that fetches via the MCP tool only (not the fixture) is expected — the fixture exists for the judge to grade against, not for the agent to read.

1. **native rewrite in Go** — output must not say "native rewriting go" or otherwise garble this; must read as TypeScript's compiler being ported to/rewritten in the Go language.
2. **Three.js** — output must not say "3.js" or "3 HTML texture"; the library name and its `THREE.HTMLTexture` API must appear correctly spelled.
3. **Traycer** (the sponsor) — output must not say "Tracer"; if the sponsor segment is mentioned at all (see the sponsor-exclusion case for whether it should be), the name must be correct.
4. **"famously bad at doing math"** — output must not invert this to "famously better at doing math." This is a meaning inversion, not a spelling slip — the single highest-severity criterion in this case. A run that gets the other four right but inverts this one fails the case.
5. **Qwik** — output must not say "Quick"; the framework name must be correct if mentioned.

A PASS requires all five terms correct. Missing a term entirely (not mentioned in the output) does not fail this specific case — only an incorrect/garbled rendering of a term that IS mentioned fails. (Completeness is graded by a separate criterion set, not this one.)

6. **Verification log present and covers these terms.** Per Method step 6's verification-log requirement (added after this case's original pilot run — see the run's own TICKETS.md proposal #1, which identified this exact gap): output includes a Verification log listing each of the 5 terms above with source consulted and outcome. A PASS on criteria 1-5 with no log present is now a FAIL on this criterion — correct-by-luck is no longer sufficient; the check must be visible, not just claimed.
