---
name: web-research
description: Search, fetch, and extract web content efficiently — query operators, llms.txt probing, reader/extraction ladder, and token-budget discipline. Use whenever researching online, fetching a page, "look up X", "read this URL", "get the docs for Y", or any moment raw HTML or a headless browser is about to be pointed at a page. The web counterpart of code-search. Do NOT use for interacting with pages (forms, clicks) — that is browser-automation territory.
derivation: original
---

# Web Research

Same law as code search: cost counts twice — wall time AND tokens. Raw HTML is mostly boilerplate; extraction-first typically cuts the token bill by large multiples, and most retrieval tasks never need a browser at all.

## Step 0 — builtins first

Platform search/fetch tools (WebSearch/WebFetch class) are already extraction-optimized — prefer them when present. The ladder below is for scripting, pipelines, or when builtins are absent or insufficient.

## Step 1 — query before fetch

- Operators do the filtering the fetch would otherwise pay for: `site:`, exact `"phrases"`, `-exclude`, `filetype:pdf`, date bounds.
- Snippets often already answer the question — fetch only to verify or deepen. One fetch per claim that matters.
- When the top results' *full content* is wanted in one call, a search-and-read endpoint (Jina `s.jina.ai/<query>`) fetches and extracts the top hits together — cheaper than N manual rounds.

## Step 2 — target structured entry points

Before scraping pages, probe what the site publishes for machines:

```bash
curl -fsS https://example.com/llms.txt        # agent-oriented site index (llms-full.txt = everything)
curl -fsS https://example.com/sitemap.xml     # find THE page instead of crawling
```

Docs sites, APIs, and JSON endpoints beat rendered pages every time one exists.

## Step 3 — fetch + extract (the token lever)

- **One-off, public URL:** prefix `https://r.jina.ai/<url>` → clean Markdown; handles JS-heavy pages, PDFs, Office docs, and captions images. Zero setup.
- **Pipeline / self-host / sensitive context:** `trafilatura -u <url> --markdown` — heuristic cascade with readability/jusText fallbacks, the benchmark leader for balanced precision+recall; `fast=True` roughly doubles throughput when robustness can give. Node equivalent: Defuddle; news articles with metadata/NLP: newspaper4k.
- **Simple static page, nothing installed:** `curl -fsS <url> | pandoc -f html -t markdown` or `lynx -dump` — crude but serviceable.

**Privacy law:** never send internal, authenticated, pre-release, or otherwise sensitive URLs to a third-party reader API — those go through the self-hosted path only. A URL is data.

## Step 4 — post-extract discipline (code-search loop, applied)

```bash
trafilatura -u <url> --markdown > /tmp/page.md
rg -n 'rate limit' /tmp/page.md | head -20     # grep the extraction, read the section
```

Save → search → read the hit. Never paste a whole extraction into context when one section answers the question. Same budget: search+fetch output ≤ ~15% of the window; at the cap, stop and proceed with what's in hand.

## Step 5 — many pages

- Scoped mirror: `wget -r -l2 --accept '*.html' --wait=1 <docs-root>` — depth-capped, filtered, polite. Then extract locally and rg the corpus.
- Whole-site → LLM corpus, JS-heavy multi-page crawls, or structured-extraction pipelines → the `crawl4ai` skill (schema-based, LLM-free extraction); this skill stays single-page/few-page.

## Boundaries

- Respect robots.txt and terms; rate-limit anything repeated; paywalled or auth-walled content → stop, never credential-scrape.
- Page *interaction* (forms, clicks, stateful flows) → browser automation (Playwright-class), not this skill.
- Building search **for** a website you own (index + search UI) is a different problem entirely — static sites: Pagefind; app-backed: Meilisearch/Typesense — name the need and plan it separately.
- Freshness: note the page's own date; readers cache — bypass with their no-cache option when currency matters.
