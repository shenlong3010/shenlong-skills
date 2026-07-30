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

## Three states

A library is mostly unread, so extraction is paid only where it earns out — and
what earns it is *reading the thing*, not its size.

| state | what it means | searchable |
|---|---|---|
| **swept** | never opened; metadata, TOC, text-layer verdict only | no |
| **focus** | sitting in the reading folder right now | yes — **default scope** |
| **reference** | finished reading, left the folder | yes, via `scope="all"` |

`ingest_dir` sweeps (cheap, samples ~5 pages). `sync_focus` promotes what is in
the reading folder: it indexes new arrivals and drops departures back to
reference. `full_index` does one document by hand.

**Nothing is ever un-indexed.** Reading a document promotes it permanently, so a
book you finished stays findable months later — you stop rereading it long
before you stop consulting it. Dropping its text to save space would make search
go quiet on a book you *know* covers the topic, which is worse than never having
indexed it: the silence looks like a real answer.

Growth is therefore bounded by what you actually read, not by a cleanup rule.
Measured at ~1.9 KB/page.

**Why the default scope is focus.** With a large corpus indexed, a query for
"caching" returns hits from every book that mentions the word, burying the one
in front of you. Scoping to what you are reading makes results relevant rather
than merely fewer. A focus-scoped search that finds nothing while the wider
corpus has hits says so explicitly and names the retry — that silent-miss case
is the one failure this design exists to prevent.

## Tools

| tool | what it gives you |
|---|---|
| `sync_focus(path)` | index what is in the reading folder; unfocus what left |
| `search_corpus(query, limit, book_id, scope)` | ranked page hits; `scope="focus"` (default) or `"all"` |
| `list_books(filter, limit)` | the corpus with each document's state |
| `get_toc(book_id)` | chapter list with pdf + printed page numbers |
| `get_pages(book_id, start, end, printed)` | full text of a page span (20-page cap) |
| `ingest_book(path)` / `ingest_dir(path)` | sweep one document / a directory |
| `full_index(book_id)` | index one document by hand |

Typical loop: `ingest_dir` the library once, then move what you are reading into
the reading folder and call `sync_focus`. Everything else follows from search.

### Blog notes — a separate lane

| tool | what it gives you |
|---|---|
| `ingest_blog(notes_path, url, source, tier, published, read_at)` | index one blog-post notes file |
| `search_blogs(query, limit, blog_id, since, source)` | ranked section hits across notes you have read |
| `list_blogs(limit, since, source)` | the reading log, newest first |
| `get_blog(blog_id, section)` | one note, whole or one section |

**Why a second pair of tables instead of a `kind` column on `books`.** bm25 is
length-normalised. A 2,400-word blog note that says "mvcc" six times outranks a
613-page book's chapter on it — shorter, not better. Ranking the two together is
a false comparison, so `blogs`/`blog_chunks` is a separate FTS index and the two
searches never mix. Run both when you want both; the results are honest
side-by-side because nothing pretended the scores were comparable.

**Identity is `(url, read_at)`, not the notes file.** Re-ingesting the same post
on the same day updates in place. The same post read months later is a new row
linked by `reread_of`, so a second read can be compared against the first
instead of overwriting it. Books get their permanence from `focus` going 1→0;
notes get theirs from never being deleted.

## Two things it gets right that are easy to get wrong

**PDF page ≠ printed page.** Front matter offsets them, so "go to page 340"
lands in the wrong place if you store only one. Both are stored, every tool
reports both, and `get_pages(..., printed=True)` accepts the number on the paper.

The offset is **measured, not guessed**. Inferring it from the TOC's first
chapter entry looked reasonable and was silently wrong on real books — many
outlines list only part names ("I Foundations") and never "Chapter 1", so the
offset defaulted to zero and every printed-page lookup drifted. `full_index`
instead votes on the page numbers printed on the pages themselves: for each
page, a number in the first or last line votes for `pdf_page - printed`. The
true offset wins by a landslide because it is the only value that agrees across
the whole book — CLRS measures 21 with 1230 of 1306 pages agreeing.

When the vote is weak the measurement is rejected **and the provisional TOC
guess is cleared**, so printed numbers fall back to pdf numbers and the tool
says so. Keeping the guess was the subtler bug: one book carried a TOC-inferred
offset of 17 while `full_index` reported that measurement had failed, leaving
every printed page number resting on an inference the tool had just disclaimed.
It happened to be correct, which is exactly what made it dangerous.

Front matter precedes printed p.1 and is usually in roman numerals, which a
single linear offset cannot express. Those pages report `front matter` rather
than a negative number.

**Search terms are quoted for you.** FTS5 treats `-` as NOT, so `red-black tree`
is a syntax error rather than a search. Bare terms are quoted into literals;
explicit `"phrases"` and uppercase `AND`/`OR`/`NOT` pass through untouched. The
tokenizer still strips `+` and `:`, so `C++` matches bare "c" — for
symbol-heavy searches, use a distinctive adjacent word.

**Text quality is decided at sweep time, not discovered later.** A scanned PDF
has no text layer, and indexing it yields *searchable nothing* — worse than no
index, because the silence looks like a real negative result. The verdict is
judged on the **best** sampled page, not the mean: front matter, part dividers,
and full-page figures are legitimately near-empty, so averaging misflags real
books. `full_index` refuses a `none` book outright and routes you to OCR;
partial extractions warn with a page count so incomplete coverage is visible.

## Why there is no companion skill

An early `read-book` skill wrapped these tools in prose — a reading procedure,
an output shape, a summarizing method. Using it against a real book showed the
prose contributed nothing: summarizing a passage is baseline model capability,
and the two behaviors that *did* matter (check the corpus before extracting;
search, then load only the hit's span) belong in the tool descriptions above,
where they fire automatically instead of costing description tokens every
session. The server is the whole artifact.

## Limits (v1, deliberate)

PDF only. Single user. Keyword search (FTS5), no embeddings — escalate to
vectors only when keyword search repeatedly misses content you know is there,
or when conceptual rather than term queries dominate. Chunking is per page, not
semantic. Re-sweep after moving files; paths are the identity key.

Requirements: `fastmcp>=3`, `pypdf>=5`.
Test: `uvx --with fastmcp --with pypdf --with reportlab python test_corpus.py`
(reportlab builds the fixture PDFs; the server itself does not need it).
