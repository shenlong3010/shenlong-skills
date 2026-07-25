# book-corpus — MCP server over a personal library

One SQLite DB indexes many books, so a library of hundreds of mostly-unread
files becomes queryable: *which of my books cover consensus*, *what does page
340 say*, *what's actually indexed*.

## Wire it

Reference this file by absolute path in `~/.claude.json` (global user scope) and
let `uvx` provision dependencies in an isolated env — no global install:

```json
{ "mcpServers": { "book-corpus": {
    "type": "stdio",
    "command": "uvx",
    "args": ["--with", "fastmcp>=3", "--with", "pypdf", "python",
             "C:/Users/you/path/to/mcp/book-corpus/server.py"] } } }
```

The CLI reads MCP config **only** from `~/.claude.json` — never `settings.json` —
and a **restart** is required before the tools appear.

DB defaults to `~/.local/share/book-corpus.db`; override with `BOOK_CORPUS_DB`.
It is created on demand and lives outside the repo — book files and the index
are never committed.

## Two-phase ingest, on purpose

A library is mostly unread, so extraction cost is paid only where it earns out:

| phase | cost | gives you |
|---|---|---|
| `ingest_dir` / `ingest_book` — **sweep** | cheap, samples ~5 pages | title, author, page count, TOC, text-layer verdict |
| `full_index` — **full text** | costly, reads every page | per-page FTS5 search inside that book |

Sweep the whole library once; `full_index` a book when you actually start
reading it. `search_corpus` only sees fully-indexed books and says so when
nothing is indexed yet, rather than returning a confident empty result.

## Tools

| tool | what it gives you |
|---|---|
| `list_books(filter, limit)` | what's in the corpus and its index state |
| `get_toc(book_id)` | chapter list with pdf + printed page numbers |
| `search_corpus(query, limit, book_id)` | ranked page hits with snippets |
| `get_pages(book_id, start, end, printed)` | full text of a page span (20-page cap) |
| `ingest_book(path)` / `ingest_dir(path)` | sweep one book / a directory |
| `full_index(book_id)` | the expensive per-page pass |

## Two things it gets right that are easy to get wrong

**PDF page ≠ printed page.** Front matter offsets them, so "go to page 340"
lands in the wrong place if you store only one. Both are stored; the offset is
inferred from the TOC's first chapter entry, every tool reports both, and
`get_pages(..., printed=True)` accepts the number on the paper.

**Text quality is decided at sweep time, not discovered later.** A scanned PDF
has no text layer, and indexing it yields *searchable nothing* — worse than no
index, because the silence looks like a real negative result. The verdict is
judged on the **best** sampled page, not the mean: front matter, part dividers,
and full-page figures are legitimately near-empty, so averaging misflags real
books. `full_index` refuses a `none` book outright and routes you to OCR;
partial extractions warn with a page count so incomplete coverage is visible.

## Limits (v1, deliberate)

PDF only. Single user. Keyword search (FTS5), no embeddings — escalate to
vectors only when keyword search repeatedly misses content you know is there,
or when conceptual rather than term queries dominate. Chunking is per page, not
semantic. Re-sweep after moving files; paths are the identity key.

Requirements: `fastmcp>=3`, `pypdf>=5`.
Test: `uvx --with fastmcp --with pypdf --with reportlab python test_corpus.py`
(reportlab builds the fixture PDFs; the server itself does not need it).
