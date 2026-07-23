---
name: read-eng-blog
description: Read an engineering or architecture blog post at full technical fidelity — fetch the text without a summarizer flattening it, read the diagrams that carry the architecture, reproduce code and named standards verbatim, and end with an honest note of what the post omits. Use whenever handed an engineering blog, architecture writeup, systems post, or "read this blog / read this post" where the substance is the design (Uber/Netflix/Stripe/Cloudflare-style eng blogs, RFC-flavored posts). Do NOT use for research papers (use paper-notes or paper-deep-dive) or conference-talk videos (use talk-notes).
derivation: original
flow: lookup
domain: web
---

# Read Eng Blog

An engineering blog's value is its detail — the named standard, the wire format, the decision and the alternative rejected, the diagram. The failure this skill prevents: a summarizing fetcher flattens that into generic prose, and the diagram carrying the architecture is never retrieved at all. This skill is the *discipline* for a high-fidelity read: get the text raw, get the figures rendered, reproduce specifics verbatim, and be honest about what the post never said.

## Step 1 — fetch text, no flattening middleman

A summarizing fetcher (WebFetch-class, backed by a small model) drops named standards, RFC numbers, and mechanics — it optimizes for gist, and gist is exactly what's not wanted here. Instead route retrieval to **web-research**'s extraction ladder: get *clean markdown* (raw fetch → article-container extraction with `bs4`/trafilatura), save it, and read the article body yourself. Save → read the section → never paste the whole page (search+read budget ≤ ~15% of context, per web-research).

## Step 2 — get the diagrams (the structural branch)

Architecture lives in the figures, and eng-blog figures are routinely **lazy-loaded via JS** — a static `curl`/`bs4` fetch sees only navigation icons and app-store badges, not Figure 1. Retrieving the article text does **not** retrieve the diagram. So branch on figure type:

- **Text-format diagram** in the source (a mermaid/plantuml block, or an `.svg` that actually contains `<text>` nodes) → route to **read-diagram**; it's text, don't screenshot it.
- **Raster or lazy-loaded figure** → render with Playwright MCP (`browser_navigate`), then **prefer the real asset over a screenshot**: `browser_evaluate` to `scrollIntoView()` the figure and read its `currentSrc` — many sites (Uber, Medium) wrap the image in a base64 resize-proxy URL that decodes to the source PNG; fetch that directly for a sharp, full-resolution asset, then downscale via **image-prep** before reading. Fall back to `browser_take_screenshot` (scoped to the element) only when there's no fetchable source. Route the resulting image to **read-image**. This is the branch a summarizing fetcher and a bare `curl` both miss.
  - **Lazy-load gotcha (verified):** an element screenshot taken before the figure scrolls into view returns a **blank white image**. Always `scrollIntoView()` and confirm the image painted (`img.complete && img.naturalWidth > 0`) *before* screenshotting or reading `currentSrc` — a blank shot that "succeeds" is the failure this skill exists to catch.
- **Figure you genuinely can't retrieve** (paywalled asset, render fails) → say so explicitly in the notes. A silently dropped diagram is the exact degradation this skill exists to stop.

## Step 3 — reproduce specifics verbatim

- Code blocks, schemas, config, and wire formats: reproduce **literally**, never paraphrase into prose. "It uses a compact binary encoding" loses the fact that it's CBOR.
- Named standards, RFCs, ISO numbers, library and API names: carry them **exactly** (`RFC 9180`, `ISO/IEC 18013-5`, `HPKE`, `PKIdentityRequest`) — they are the searchable handles a reader needs.

## Step 4 — write the notes file

Persist the read as a notes file (default `notes/eng-blogs/<slug>.md`; ask once if the repo has no obvious notes dir) — matching the **paper-notes** / **talk-notes** pattern, so a daily reading habit leaves a durable, greppable trail rather than vanishing into chat. Sections:

- **Problem** — what forced this work, why it mattered.
- **Architecture** — components + data flow, *incorporating the diagram read in Step 2*, not its alt-text.
- **Key decisions & tradeoffs** — for each: the decision, the alternative rejected, and why. This is the substance; a list of components without the *why* is a degraded read.
- **Standards / refs / tech** — verbatim (Step 3).
- **Code / schemas** — reproduced (Step 3).
- **What the post omits** — mandatory honest line, in the spirit of read-image's Uncertainties line. E.g. "architecture writeup only — no scale/throughput numbers, no code." Naming the gap is the difference between a limit of the post and a failure of the read.

Output is full technical prose **regardless of caveman level** — this read *is* the deliverable, so it stays uncompressed the way code and commits do. (If a whole reading session should run terse-free, the user sets `/caveman lite` or a session default; a skill cannot switch caveman itself.) A long post plus a diagram screenshot is also a clean **background sub-agent** job — offer it to keep the main session context lean.

## Boundaries

- Fetch/extract mechanics (the raw-fetch ladder, llms.txt, reader APIs) → **web-research** — this skill orchestrates it, doesn't restate it.
- A figure *image* → **read-image**; a diagram *file* (.mmd, .puml, text `.svg`) → **read-diagram**.
- Research paper → **paper-notes** (relevance verdict) or **paper-deep-dive** (method + math).
- Conference-talk video / YouTube → **talk-notes**.
- Multi-page doc-site crawl or a structured-extraction pipeline → **crawl4ai**, not a per-page read.
