---
name: daily-blog
description: Pick one worth-reading engineering blog post from 60 verified feeds and read it at full fidelity, so a finished read is waiting at the next session start. Use for "what should I read today", "daily blog", "prepare tomorrow's read", "any good engineering posts", or when wiring the SessionEnd/SessionStart daily-read hooks. Do NOT use when handed a specific URL — that is read-eng-blog directly; not for multi-page crawls (crawl4ai) or paper feeds (paper-notes).
derivation: original
flow: lookup
domain: web
---

# Daily Blog

A reading habit dies from two things: not knowing what to read, and waiting for it. This skill kills both — it selects one post worth full-fidelity attention from a verified feed list, reads it via **read-eng-blog**, and leaves the finished notes on disk so the session that *displays* it waits on a file read, not a fetch.

The selection step is the real work. At 60 feeds the daily candidate pool is mostly announcements, release notes, and org news. Reading a weak post costs the same as reading a good one, so triage is what makes the habit sustainable.

## Mode: prepare

Runs unattended (detached, from the `SessionEnd` hook) or manually. Writes `notes/daily-blog/pending.md`.

### 1 — fetch the feeds

`assets/feeds.json` holds the verified list (`feeds[]`, each with `name`, `feed`, `tier`). Fetch all in parallel; 60 feeds complete in about 5s, so fetch cost is not worth optimizing.

Per feed: `curl -sSL --max-time 20 --range 0-524287 -A '<browser UA>'`.

- **`--range`, not `--max-filesize`.** `--max-filesize` *aborts and deletes* the partial file, so a large live feed reports as empty — measured: it made Marc Brooker's 1.6 MB feed look dead. `--range` yields the first 512 KB. Servers that ignore `Range` send everything, so cap client-side too.
- **Retry truncated feeds once at 2 MB when they yield <5 items.** 512 KB is not universally enough: measured, Dan Luu's 11 MB feed yields only **2 items** in the first 512 KB because a single post fills the cap, while Brooker's yields 48. A feed that was truncated *and* came back thin is under-sampled, not small — refetch with `--range 0-2097151` before giving up on it.
- Non-200 is a **skip, not an error** — feeds rot. Log the skip and continue.
- A real browser UA matters: at least one publisher returns 406 to default curl.

### 2 — parse

**Use `defusedxml.ElementTree`, never stdlib `xml.etree`.** These are 60 untrusted third-party XML documents parsed in an unattended background process. Verified on Python 3.14: stdlib rejects *external* entities (so XXE is not the exposure) but **does expand internal ones** — a 3-level billion-laughs bomb expanded to 3000 chars, and real bombs use 9-10 levels. `defusedxml` blocks entity expansion outright. Install it if absent (`pip install defusedxml`); it is the one non-stdlib dependency here and the tradeoff is memory-exhaustion safety in a process nobody is watching.

Handle both dialects — RSS `<item>` with `<link>` and `<pubDate>`, Atom `<entry>` with `<link href>` and `<updated>` under `{http://www.w3.org/2005/Atom}`. Extract **title, link, date only**; discard body text immediately even when the feed inlines it (Dan Luu's feed is 11 MB of full post text).

Truncation at 512 KB leaves a malformed document, so parse defensively: on `ParseError`, salvage complete `<item>`/`<entry>` elements by regex rather than discarding the feed. Several large feeds only ever parse via this path.

### 3 — filter what's already read, with an expiry

`notes/daily-blog/.state.json` holds `{"seen": {url: "YYYY-MM-DD"}, "shown": ..., "prepared": ...}` — `seen` is a **map of URL to read-date, not a flat list**, because entries expire.

Drop any candidate read within the last **45 days**. Past that, a post becomes eligible again: the genuinely good ones are evergreen and worth a second pass once the details have faded, and a permanent `seen` list would monotonically shrink the pool until the feed starves. On re-selection, mark it in `pending.md` as a **re-read**, with the original read date and a pointer to the existing dated notes file, so the second read can be compared against the first rather than duplicating it.

Prefer items published in the last ~10 days; fall back to older unread ones only if nothing recent survives triage.

### 4 — triage for decision density

Score each candidate on the title, plus `tier` as a prior (tier 1 gets benefit of the doubt; tier 2 must earn it).

**Reject outright** — these are the noise the broad feed list buys: "now generally available" / "GA in", region and availability announcements ("now supports eu-west-2"), release notes and version bumps, hiring and org news ("we're hiring", "intern cohort", "welcome our new"), event and conference promos ("Bug Bash is coming to Europe"), award and analyst news ("named a Leader in the Gartner Magic Quadrant"), funding and money milestones ("$100 million for open source"), partnerships, pricing changes, pure product marketing.

**Favour** — the shapes that carry an actual engineering decision: post-incident and postmortem writeups (reality, not plans), migrations ("we moved X to Y" — these always name the rejected alternative), removals and reversals ("we deleted", "why we moved back"), internals deep-dives, "how we made X N times faster" with a mechanism, and design-tradeoff arguments.

**A second source on a story already read is a BOOST, not a penalty.** When two companies write about one incident, that is two sets of engineering decisions, not a duplicate: the researcher documents the attack chain, the provider explains what they are changing about their sandbox. The second perspective is the payoff. So if a candidate's title overlaps strongly with something in `seen`, and the **source differs**, add to its score — a known-interesting topic with fresh decisions in it beats an unknown topic. Only an identical URL is skipped, and step 3's 45-day rule handles that.

**Favour blogs of widely used open-source products.** A project whose product thousands of people run writes about decisions with real consequences — inference batching, storage formats, runtime tradeoffs — and the reader can go look at the code. Hugging Face, vLLM, DuckDB, Deno, Astral, PyTorch, Rust, Go, Tailscale, Kubernetes and Bun are in the list for this reason. Treat "this project ships something I could `pip install` or `docker run`" as a positive signal, distinct from company size.

**Two favour-patterns need narrowing — both produced false positives on the first real dry run over 179 candidates:**

- Never match a bare `bug`. It hit "**bug bounty** program" (policy news) and "**Bug Bash** is coming to Europe" (event promo), scoring both at 7. Require the bug to be *found or fixed*: "we found", "we tracked down", "the weird/subtle/nasty bug", "bug that", "race condition", "heisenbug".
- Never match a bare `million`/`billion`. It hit "**$100 million** for open source" (funding milestone) at 6. Require a technical unit beside the magnitude — "1 million concurrent **sandboxes**", "trillions of **messages**", "billions of **vectors**".

Both fixes were verified by re-running the dry run: the three false positives disappeared and the rejected pile grew 21 → 24, with no true positive lost.

Pick the single highest scorer.

### 5 — if nothing clears the bar, say so

Write a `pending.md` that reports the empty day: what was rejected and why (name the posts), plus the next archive candidate the user could force. **Do not silently read a weak post.** An honest empty day keeps the feed trustworthy; a padded one teaches the reader to skim past it.

Also say so if the live feed pool drops below ~10 — that means feed rot has quietly narrowed the funnel and the list needs re-verifying.

### 6 — read the winner

Invoke **read-eng-blog** on the chosen URL. Do not restate its method here — it owns fetch-without-flattening, the figure branch, verbatim reproduction, and the "what the post omits" line.

**Link-blog branch — check before reading.** Some tier-1 sources (Simon Willison especially) publish commentary that quotes another writeup rather than original work. Because triage scores the *title*, such a post inherits the primary document's score: on the first real run, a ~500-word commentary scored 13 on the strength of Hugging Face's incident-timeline title.

If the fetched page is chiefly commentary on another source, decide and say which:

- **Follow through to the primary** when the commentary is a pointer and the primary is the engineering document. That is usually the better read, and the day's notes should say the selection came via a link blog.
- **Read the commentary** when its own analysis is the value (added attributions, industry framing). Then label it explicitly as commentary, name the primary URL, and keep quoted material distinct from the author's assertions.

Either way the notes must not present a summary of someone else's writeup as if it were the original.

**Fidelity floor.** A 500-word commentary yields thinner notes than a 5,000-word writeup, and that is a fact about the source, not a failed read. Say so in the notes rather than padding to look complete — but if the winner turns out to be *substanceless* on fetch (a stub, a redirect, a paywall), treat it as a failed candidate and fall back to the next-highest scorer rather than writing thin notes about nothing.

### 7 — write pending.md

A short header block (source name, post title, URL, publish date, why it was selected) followed by the **complete** read-eng-blog notes.

Then update state: **add the URL to `seen` with today's date as its value** (`seen[url] = "YYYY-MM-DD"` — it is a map, and the 45-day expiry in step 3 reads those dates; appending a bare string breaks expiry silently), and set `prepared` to today.

**`pending.md` is the only notes file this mode writes.** read-eng-blog step 4 would otherwise persist its own copy to `notes/eng-blogs/<slug>.md` — skip that here, since `show` mode rotates `pending.md` into `notes/daily-blog/<date>.md` and that dated file *is* the durable trail. Two copies of the same read is duplication, not a backup.

### 8 — index the dated notes file for search

Once `show` has rotated `pending.md` into `notes/daily-blog/<date>.md`, index it via the **book-corpus** MCP server:

```
ingest_blog(notes_path="notes/daily-blog/<date>.md",
            url=<the post URL>, source=<feed name>, tier=<1|2>,
            published=<post date>, read_at=<date>)
```

`grep` over `notes/` is fine at three files and painful at sixty — which is one month of this habit. Indexing each read as it lands means the search exists before you need it.

- **Index the dated file, never `pending.md`.** `pending.md` is renamed on display, so indexing it would store the same read twice under two titles. Step 7 writes it; step 8 runs after the rename.
- **`url` is the identity, not the file path.** Re-running the same day updates in place; the same URL read months later becomes a new row linked by `reread_of`, so two reads can be compared instead of one overwriting the other. That is what makes the 45-day re-read in step 3 useful rather than destructive.
- **Blog notes go in `blogs`/`blog_chunks`, never `books`/`chunks`.** bm25 is length-normalised, so a 2,400-word note that says "mvcc" six times outranks a 613-page book's chapter on it — shorter, not better. `search_blogs` and `search_corpus` stay separate so that false comparison cannot be made; run both when you want both.

Output stays full technical prose regardless of caveman level — the read *is* the deliverable, same rule read-eng-blog states.

## Mode: show

What the `SessionStart` hook does, in bash, without invoking this skill — `SessionStart` blocks the first prompt until its hook exits, so display must stay a sub-50ms file operation. Print `pending.md`, rename it to `notes/daily-blog/<today>.md`, stamp `shown`. Documented here for manual use and so the hook's behaviour lives beside the skill it serves.

## Gotchas

- **Feed URLs guessed from memory are wrong about half the time.** Measured while building `assets/feeds.json`: 20 of 48 guessed URLs were dead, and six sites (TigerBeetle, Modal, ClickHouse, Materialize, Render, incident.io) only resolved via HTML `<link rel="alternate" type="*xml*">` autodiscovery after multiple path guesses had 404'd. **Ask the page, don't guess the path** — and re-verify before editing the list.
- **Many modern blogs publish no feed at all.** Figma, PlanetScale, Uber, Shopify, Notion, LinkedIn and others have no discoverable feed; `_dropped` in `assets/feeds.json` records each with the evidence, so a future re-check doesn't repeat the search. Uber specifically returns **406 to non-browser user agents**.
- **A 200 response is not a feed.** JS-rendered blogs return HTML with status 200 for `/rss.xml`. Validate that the body parses and yields ≥1 item; status alone passes garbage through.
- **`Start-Process` is the Windows detach.** `setsid` does not exist in Git Bash on Windows, so a POSIX detach silently spawns nothing (verified: the child never ran, and the failure was invisible). Use `powershell Start-Process -WindowStyle Hidden` there; `setsid nohup … &` on Linux. Detached-process survival past session exit is **undocumented** in Claude Code — the hooks carry a visible-failure fallback rather than assuming the spawn wins.
- **Hook recursion is the expensive bug.** A `SessionEnd` hook that spawns `claude -p` produces a child whose own `SessionEnd` spawns another, unattended, forever. The guard is verified empirically: a headless child reports `CLAUDE_CODE_CHILD_SESSION=true` and `CLAUDE_CODE_ENTRYPOINT=mcp-stdio-cli`, while an interactive session reports unset and `cli`.
- **`Stop` is the wrong hook event.** It fires after every agent response, not at session end — dozens of times per session. `SessionEnd` is the session-exit event, but it has a ~1.5s shared budget (raisable to 60s), so it can only *launch* a 60-90s read, never contain it.
- **Title-based triage cannot tell a writeup from a link to one.** Measured on the first real run: Simon Willison's ~500-word link-blog commentary scored **13** — the highest of 179 candidates — because the title it carried was Hugging Face's incident-timeline title. The score was real; the attribution wasn't. Step 6's link-blog branch exists for this, and it is why a high score is not by itself evidence the page holds the substance.
- **A feed can die between two runs in the same session.** Val Town's `feed.xml` verified at 109 items and 404'd minutes later; Rachel by the Bay parsed once, then began returning 302 into a connection timeout. Both are recorded in `_dropped`. Treat the feed list as perishable inventory, not configuration — the pool-below-10 warning in step 5 is the tripwire.

## Boundaries

- A specific URL to read → **read-eng-blog**. This skill picks the URL and calls it; it never reimplements the read.
- Fetch/extraction mechanics beyond RSS → **web-research**.
- Multi-page crawl or structured extraction pipeline → **crawl4ai**.
- Research-paper feeds → **paper-notes** / **paper-deep-dive**.
- Conference-talk video → **talk-notes**.
