---
name: recall-drill
description: Turn accumulated reading notes into active-recall practice — generate atomic question cards from notes/ (paper-notes, talk-notes, read-eng-blog output), run graded drill sessions, and reschedule misses. Use for "drill me on this", "make cards from my notes", "quiz me on what I've read", "what should I review today", or when rereading feels like the only way to remember. Do NOT use for live mock interviews (`interview-drill`) or for building understanding in the first place (`concept-explain`).
derivation: original
flow: career
domain: career
---

# Recall Drill

Reading leaves a trace, not a memory — unless it's retrieved. This skill converts your existing notes corpus into retrieval practice and keeps a schedule so retention doesn't depend on motivation.

## Deck and schedule format

One markdown file per deck under `notes/recall/<topic>.md`. Cards are table rows; the schedule lives with the card:

```markdown
| id | due | interval | q | a | source |
|----|-----|----------|---|---|--------|
| k1 | 2026-08-25 | 7 | Why does stdlib xml.etree still risk billion-laughs? | Rejects *external* entities but expands internal ones; defusedxml blocks expansion outright. | [[notes/eng-blogs/xml-pitfalls]] |
```

- `due`/`interval` are plain dates/integers — no dependencies, grep-friendly, diff-able.
- `source` links back to the originating note; a card whose source dies gets re-verified or deleted, never orphaned.

## Method

1. **Source selection:** pick notes worth retaining — paper-notes/talk-notes verdicts marked relevant, read-eng-blog posts you acted on, book-corpus highlights. Not everything; notes you never rated are noise until proven otherwise.
2. **Card generation — atomic only.** One fact/mechanism/tradeoff per card. Prefer *why/how* questions ("why does nearest-wins make fat-jar ordering matter") over bare *what* lookups ("what does this flag do"). Numbers and API shapes become cloze ("py-spy records at ___ without instrumentation" → sampling). Paraphrase from the note — verbatim cards test recognition, not recall.
3. **Session flow:** show `q` → attempt out loud or in writing *before* looking → self-grade honestly:
   - **miss** → interval reset to 1 day
   - **fuzzy** (got it with effort/half) → interval ×2
   - **clean** → interval ×3, capped at ~60 days
   Update `due` = today + new interval. Grade the *attempt*, not the reading.
4. **Deck hygiene per session:** overdue cards first, then new cards (≤10/session — more is cramming wearing a costume); delete cards you can now answer trivially *and* re-derive from first principles — drilling what's cheap to recompute wastes sessions.

## Gotchas

- **Recognition ≠ recall.** Multiple-choice feels productive because it always succeeds. Free recall or short written answers only; multiple choice is allowed as a *fallback* prompt when a card has missed three times.
- **The illusion from rereading:** highlighted notes feel familiar precisely because they're familiar. Familiarity is the enemy this skill exists to fight — if an answer comes "because I just read it", grade fuzzy, not clean.
- **Cards without sources rot silently.** An unsourced card that contradicts the library's current reality trains a bug. Every card carries its `source`; stale-source cards get re-verified before they're trusted again.

## Boundaries

- `interview-drill` runs scenario interviews with follow-up pressure — use it once the factual base here is solid; drilling facts and rehearsing synthesis are different reps.
- `concept-explain` builds the mental model the first time; this skill assumes it and maintains it.
