# Auditing CLAUDE.md files

## Inventory
All CLAUDE.md load and concatenate, root-to-cwd, plus each dir's `CLAUDE.local.md`:
managed policy → user (`~/.claude/CLAUDE.md`) → project files from filesystem root
down to cwd. More specific wins on contradiction. Enumerate every file in the
chain before judging any single one — a rule that looks redundant may be the
override of a broader one above it.

## Token efficiency (biggest lever)
CLAUDE.md loads **every session, in full** — it's the standing memory bill.
- Flag stale entries: dated notes whose fix already shipped, "pending" items long
  done, TODOs for removed code. Convert or delete.
- Flag prose that restates a general rule already in a parent file — the child
  should only carry what's *more specific*.
- Flag long narrative where a rule would do. A rule names the constraint; a story
  costs tokens every session to re-read.
- Measure: the caveman-plugin eval data shows "Answer concisely." scores no better
  than no instruction — a useful instruction names the specific structures to cut.
  Same for CLAUDE.md: vague exhortations are dead weight; concrete rules earn their
  tokens.

## Self-contradiction and drift
- Two files in the chain giving opposite instructions (the more-specific wins, but
  flag it — the author may not know).
- A CLAUDE.md rule that contradicts an active output-style/injector (e.g. "be
  terse" vs an output style demanding Insight blocks). Cross-check against
  `references/injectors.md`.
- A rule referencing a file/flag/hook that no longer exists — verify every named
  artifact still exists before trusting the rule.

## The memory-vs-hook boundary (common miscategorization)
"From now on, whenever X, do Y" is an **automated behavior** — it belongs in a
hook (the harness executes hooks, not the model reading memory). A CLAUDE.md rule
can't reliably fire on an event. Flag automation-shaped instructions living in
CLAUDE.md and route them to `update-config` / a hook. Conversely, flag one-shot
facts wired as hooks that should just be memory.

## Structure checks
- Hard constraints stated first and unmissable (the "read first" pattern).
- Per-directory guides carry only that directory's conventions; globals stay in the
  root and aren't restated.
- Machine-specific env facts (paths, shell dialect, encoding) present where the
  platform is nonstandard — their absence is a silent-failure source.

## Enhancement
- A repeatedly-relearned lesson from the session/transcript not yet captured → add
  it (concise rule + the why).
- A dangerous default (destructive op, push, spend) with no reversibility rule → add one.

## Route the rewrite out
This pass **flags** CLAUDE.md issues as part of a whole-setup audit. A full rewrite
or template-conformance pass is `claude-md-improver`'s job — hand it the flagged
list rather than rewriting here.
