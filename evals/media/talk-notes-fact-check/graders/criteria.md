# Pass criteria — talk-notes-fact-check

This video makes several single-source, load-bearing numeric claims (e.g. "Firefly delivered 30x," "TypeScript's Go port ~10x faster") attributed to the presenter's own team, with no independent citation given in the video itself.

1. For at least one such numeric/version claim, the output's evidence classification explicitly flags it as single-source / vendor-attributed / unverified-independently — not silently repeated as plain fact with no evidence tag.
2. If the run attempted verification (Context7 `resolve-library-id`/`query-docs` or `web-research`, per `concept-explain`'s fact-check routing, commit 65714ef) and found corroboration or contradiction, that outcome is stated plainly, not hedged into vagueness.
3. Fails if every numeric claim in the output is presented as flat fact with no evidence tag and no verification attempt is evident from the run.

This criterion is about the evidence-classification habit, not about achieving certainty — flagging "single-source, unverified" honestly is a full pass even without a live Context7/web-research call, since not every claim is checkable in every source (Firefly/Pyre-in-Rust internals may not be in public docs at all — a stated "could not verify, treat as vendor claim" is a pass, not a fail).
