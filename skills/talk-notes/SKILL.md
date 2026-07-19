---
name: talk-notes
description: Turn a tech talk or video into structured notes plus a relevance-to-my-stack verdict — transcript in, decisions out. Use for "summarize this talk", "notes on this video", "watch this for me", "is this talk worth my time", or any YouTube/conference-talk URL that needs digesting. Pulls transcripts via the youtube-transcript MCP tools when available; accepts pasted transcripts otherwise.
derivation: original
flow: lookup
domain: media
---

# Talk Notes

## Purpose
The video counterpart of `paper-notes`: extract what a talk actually claims and whether it matters to the user's stack, without the hour of watching. Transcript is the source — never summarize a talk from its title and description alone; that produces confident notes about a talk nobody read.

## Method
1. **Get the transcript.** youtube-transcript MCP tools if connected; else ask for a pasted transcript or use the video's own transcript feature. No transcript obtainable → say so and stop — do not synthesize from metadata.
2. **Budget check.** A 1-hour talk ≈ 8–12k words. Over ~15 minutes of content, process in segments and carry forward a running outline instead of loading the whole transcript at once (search-output law applies: keep working set small).
3. **Skip the filler deliberately**: sponsor reads, intro banter, "like and subscribe", Q&A logistics. Note where Q&A *content* starts — it often contains the most honest material in the talk.
4. **Extract into the fixed shape:**
   - **Metadata** — speaker, event/channel, year, length.
   - **Thesis** — the one claim the talk exists to make.
   - **Sections** — outline with rough timestamps, one line each.
   - **Key claims** — each with the speaker's evidence (benchmark, war story, demo) and a flag when a claim is asserted without support.
   - **Actionable takeaways** — things the listener could adopt this week, if any.
   - **Verdict** — relevance to the user's stack and level: watch fully / notes suffice / skip, with one sentence why.

## Gotchas
- **Auto-captions mangle jargon** — "Kubernetes" becomes "cooper netties", library names arrive misspelled, and captions carry no punctuation. Treat every technical term as suspect until cross-checked against the video description, slides, or a quick search; never propagate a caption-spelled name into notes as fact.
- **Captions carry no speaker attribution** — panel talks and interviews blend voices into one stream. Flag multi-speaker content and attribute claims only when the transcript context makes the speaker unambiguous.
- **Timestamps drift** on auto-generated transcripts; treat them as ±30s pointers, not citations.
- **Conference talks front-load 5–10 minutes of credentials and agenda** — the thesis usually lands after it; don't let the intro segment dominate a segment-budgeted read.
- **No English track ≠ no transcript.** Some videos carry only manual caption tracks in other languages (the fetch error lists what exists); the MCP wrapper cannot request YouTube's auto-translate. Fetch a manual track (they translate the same audio faithfully) and translate while extracting — never give up on the video, and never silently present translated notes without saying which track they came from.

## Boundaries
Written papers/blog posts → `paper-notes` (same output shape, different source). Web pages → `web-research`. Reading slides from a screenshot → `read-image`. This skill never *interacts* with the video platform (playlists, comments) — that would be browser-automation territory.
