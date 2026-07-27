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
5. **Fact-check load-bearing claims.** For any claim citing a specific number, version, or documented product behavior (benchmark results, "X is Y times faster," a named API's capabilities), route the check the way `concept-explain` does: Context7 (`resolve-library-id` → `query-docs`) for documented library/product behavior, `web-research` for internals or claims Context7 won't cover. A single-source vendor claim with no independent corroboration gets flagged as such in the Key Claims evidence tag, not silently repeated as fact. This is separate from the jargon-flagging gotcha below — jargon-flagging catches transcription errors, this catches unverified claims.
6. **Verify every proper noun before it goes in the notes, as a required pass — not an aside.** After drafting (step 4) and before finalizing, list every proper noun the draft mentions (library, framework, tool, sponsor, product, language, API/method name) and check each one:
   - If the auto-caption spelling isn't a recognizable real-world name (unexpected case, spacing, or a common-word substitute for what should be a brand name — "3.js", "cooper netties", "Quick" for a framework, "Tracer" where context suggests a coding-agent product), search or check the description for the real name before writing it into notes.
   - Do this even when the spelling looks plausible on its own — auto-captions substitute one real word for another (a sponsor segment naming a product is exactly where this bites: "Tracer" reads as a normal English word, not obvious jargon, and would sail past a scan looking only for "garbled-looking" text).
7. **Re-read every comparative/superlative claim about a subject's ability before finalizing** ("better at," "worse at," "faster than," "the best," "famous for") — auto-captions can flip a negation or comparison into its opposite without leaving any spelling evidence ("famously bad at doing math" → "famously better doing math" is fully grammatical either way). A claim in this shape is a required check, not an optional cross-reference: search for the phrase alongside the topic (e.g. "JavaScript famously bad at math") to confirm the polarity the speaker actually asserted before it goes in Key Claims. If the polarity can't be confirmed, flag it as uncertain rather than picking the caption's version by default — silently keeping the caption's polarity is the single worst failure mode this skill can produce.

## Gotchas
- **Auto-captions mangle jargon — verification of every proper noun is mandatory, not advisory.** "Kubernetes" becomes "cooper netties", library names arrive misspelled ("Three.js" → "3.js", "THREE.HTMLTexture" → "3 HTML texture"), framework names collide with common words ("Qwik" → "Quick"), and sponsor/product names read as ordinary English ("Traycer" → "Tracer"). Method step 6 is not optional cross-checking on suspicion — run it on every proper noun in the draft, even ones that don't look broken, because several of these garbles produce a plausible-looking wrong word rather than an obviously mangled one. Never propagate a caption-spelled name into notes as fact.
- **Meaning inversions are the highest-severity jargon failure and look nothing like a spelling error.** Auto-captions have flipped "famously bad at doing math" into "famously better doing math" — fluent, ungarbled, and wrong. A term-by-term jargon scan will not catch this because there's no odd spelling to notice; only Method step 7 (checking comparative/superlative claims specifically) catches it. Treat any claim about a language/tool being notably good, bad, fast, or slow at something as needing this check before it's repeated as fact.
- **Captions carry no speaker attribution** — panel talks and interviews blend voices into one stream. Flag multi-speaker content and attribute claims only when the transcript context makes the speaker unambiguous.
- **Timestamps drift** on auto-generated transcripts; treat them as ±30s pointers, not citations.
- **Conference talks front-load 5–10 minutes of credentials and agenda** — the thesis usually lands after it; don't let the intro segment dominate a segment-budgeted read.
- **No English track ≠ no transcript.** Some videos carry only manual caption tracks in other languages (the fetch error lists what exists); the MCP wrapper cannot request YouTube's auto-translate. Fetch a manual track (they translate the same audio faithfully) and translate while extracting — never give up on the video, and never silently present translated notes without saying which track they came from.
- **"IP blocked" from the transcript tool usually means throttled, not banned.** `youtube-transcript-api` collapses every non-200 from the timedtext endpoint into one message naming cloud-provider IP bans — it fires identically for short-window rate limits. Retry the same URL once after ~30s before believing it; one video failing and another succeeding minutes apart on the same network is a throttle, not a block. Do not diagnose the network, restart the MCP server, or fall back to browser automation until a retry has failed — the browser's own transcript panel calls the same throttled backend and hangs on "loading" forever, which looks like a separate bug and is not one.
- **Prefer the manual caption track when notes will be kept.** The MCP tool returns whatever track YouTube serves first, usually auto-captions — the source of the mangled jargon and meaning inversions above. The tool cannot select a track. When the notes are durable rather than throwaway, take the manual track from the video's own transcript panel instead — it is punctuated, correctly spelled, and timestamped. This is a preference, not a substitute for Method steps 6–7: when only the auto-caption track is reachable (rate limits, browser automation unavailable), those verification steps are what stand between the notes and a wrong or inverted claim. State which track the notes came from.

## Boundaries
Written papers/blog posts → `paper-notes` (same output shape, different source). Web pages → `web-research`. Reading slides from a screenshot → `read-image`. This skill never *interacts* with the video platform (playlists, comments) — that would be browser-automation territory.
