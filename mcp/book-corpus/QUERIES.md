# Querying the corpus DB by hand

DB: `~/.local/share/book-corpus.db` (Windows: `C:\Users\<you>\.local\share\book-corpus.db`)

A single-file SQLite DB. Any SQLite client opens it; nothing needs to be running.

## Client

**DB Browser for SQLite** is the right weight for this — purpose-built, opens a
file directly, has a Browse Data tab and an Execute SQL tab.

```
winget install DBBrowserForSQLite.DBBrowserForSQLite
```

DBeaver also works and is worth it *only if you already run it* for other
databases; it is a JDBC IDE aimed at remote servers, which is more machinery
than a 7 MB local file needs. The `sqlite3` CLI is enough for most of these
queries and ships with many toolchains (not on PATH by default on Windows).

## What is actually yours

Two tables:

- **`books`** — one row per document (PDFs and text docs alike)
- **`chunks`** — one row per page (PDF) or section (text), FTS5-indexed

The five **`chunks_*`** tables (`_data`, `_idx`, `_content`, `_docsize`,
`_config`) are FTS5's internal storage. They look like binary garbage and are
not meant to be read or edited by hand. Leave them alone.

`books` columns: `id, path, title, author, pages, page_offset, toc_json,
text_quality, swept_at, full_indexed_at, file_size, file_mtime, focus`.

`focus=1` means the document is in the reading folder right now and is what
`search_corpus` looks at by default. `focus=0` with a non-null `full_indexed_at`
is a *reference* document — finished, still searchable via `scope="all"`.

## Everyday queries

```sql
-- What is in the corpus, biggest first, by state
SELECT id, title, pages, text_quality,
       CASE WHEN focus = 1 THEN 'focus'
            WHEN full_indexed_at IS NOT NULL THEN 'reference'
            ELSE 'swept' END AS state
FROM books ORDER BY pages DESC LIMIT 20;

-- What am I reading right now
SELECT id, title, pages FROM books WHERE focus = 1;

-- What have I finished but can still search
SELECT id, title, pages FROM books
WHERE focus = 0 AND full_indexed_at IS NOT NULL ORDER BY title;

-- One line of corpus state.  NOTE: `indexed` is a reserved word — quote it or
-- alias to something else, or you get a bare "syntax error".
SELECT COUNT(*) AS docs,
       SUM(pages) AS pages,
       SUM(CASE WHEN full_indexed_at IS NOT NULL THEN 1 ELSE 0 END) AS full_text,
       SUM(CASE WHEN text_quality != 'ok' THEN 1 ELSE 0 END) AS poor_text
FROM books;

-- Which documents are searchable right now
SELECT b.id, b.title, COUNT(c.rowid) AS chunks
FROM books b JOIN chunks c ON c.book_id = b.id
GROUP BY b.id ORDER BY chunks DESC;

-- Scanned or thin-text documents (search will not find their content)
SELECT id, title, pages, text_quality FROM books
WHERE text_quality != 'ok' ORDER BY pages DESC;

-- Swept but never full-indexed: the backlog worth indexing
SELECT id, title, pages FROM books
WHERE full_indexed_at IS NULL ORDER BY pages DESC LIMIT 20;
```

## Full-text search by hand

FTS5 needs `MATCH`, not `LIKE`, and the join carries the title:

```sql
SELECT b.title, c.pdf_page,
       c.pdf_page - b.page_offset AS printed_page,
       snippet(chunks, 0, '>>', '<<', ' … ', 12) AS hit
FROM chunks c JOIN books b ON b.id = c.book_id
WHERE chunks MATCH '"dynamic programming"'
ORDER BY rank LIMIT 20;
```

**Quote your terms.** FTS5 reads `-` as NOT and chokes on `+` and `:`, so
`red-black tree` is a syntax error while `"red-black" "tree"` works. The
`search_corpus` tool quotes automatically; hand-written SQL does not.

```sql
-- Which books mention a topic at all, ranked by how often
SELECT b.title, COUNT(*) AS hits
FROM chunks c JOIN books b ON b.id = c.book_id
WHERE chunks MATCH '"consensus"'
GROUP BY b.id ORDER BY hits DESC;

-- Read one page's full text
SELECT text FROM chunks WHERE book_id = 2 AND pdf_page = 380;
```

## Page numbers

`pdf_page` is the physical page; the printed number is
`pdf_page - page_offset`. The offset is measured during `full_index` by voting
on the numbers printed on the pages, and is 0 when it could not be measured
(text documents always, PDFs without consistent numbering). Pages before
printed p.1 are front matter and go negative under the arithmetic — the tools
report them as `front matter` rather than a negative number.

## Reading toc_json

Stored as JSON text. SQLite's JSON1 functions parse it:

```sql
SELECT value ->> 'title' AS section, value ->> 'pdf_page' AS page
FROM books, json_each(books.toc_json)
WHERE books.id = 2;
```

## Safe to edit?

Reading is always safe. If you write, prefer the tools — they keep `books` and
`chunks` consistent. In particular, deleting a row from `books` orphans its
chunks (there is no cascade); delete from `chunks` first, or just re-sweep with
`force=True`.
