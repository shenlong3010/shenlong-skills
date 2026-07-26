#!/usr/bin/env python3
"""book-corpus — MCP server over a personal library of books.

One shared SQLite DB indexes many books. Two-phase ingest by design:

  sweep      (cheap, all books)  -> title, author, pages, TOC, text quality
  full_index (costly, on demand) -> per-page chunks into an FTS5 table

The split exists because a library is mostly unread: you want "which of my
books cover consensus?" answerable across hundreds of files without paying
extraction cost on all of them, and "what does page 340 say?" only for the
book actually being read.

Page numbering: PDF page index != printed page number (front matter offsets
them). Both are stored; `printed` is the number on the paper, `pdf_page` is
the 1-based physical index. Every tool reports both.

Text quality is recorded at sweep time, not discovered later: a book whose
text layer is empty would otherwise be indexed as searchable nothing.

Run:  python server.py
Wire: see README.md (uvx --with fastmcp, absolute path, ~/.claude.json)
"""
import json
import os
import re
import sqlite3
import time
from pathlib import Path

from fastmcp import FastMCP
from pypdf import PdfReader

mcp = FastMCP("book-corpus")

DB_PATH = Path(
    os.environ.get("BOOK_CORPUS_DB", Path.home() / ".local" / "share" / "book-corpus.db")
)
PDF_EXTS = {".pdf"}
TEXT_EXTS = {".md", ".markdown", ".txt", ".rst"}
BOOK_EXTS = PDF_EXTS | TEXT_EXTS
TEXT_CHUNK_CHARS = 3000     # ~a page of prose; keeps get_pages spans meaningful
MAX_PAGE_SPAN = 20          # get_pages hard cap — an unbounded span dumps a chapter
MAX_HITS = 50               # search_corpus cap — context is the scarce resource
SNIPPET_CHARS = 240
# Text-layer verdict thresholds, judged on the BEST sampled page, not the mean:
# a book's front matter, part dividers, and full-page figures are legitimately
# near-empty, so averaging misflags real books as scanned. One page with real
# text proves the text layer exists.
TEXT_OK_BEST_PAGE = 200     # >= this on any sampled page -> a genuine text layer
TEXT_SPARSE_FLOOR = 1       # some text, but thin everywhere -> partial/mixed scan


# ---------------------------------------------------------------- storage

def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY,
        path TEXT UNIQUE NOT NULL,
        title TEXT, author TEXT,
        pages INTEGER,
        page_offset INTEGER DEFAULT 0,   -- printed = pdf_page - page_offset
        toc_json TEXT,
        text_quality TEXT,               -- ok | sparse | none | error
        swept_at REAL,
        full_indexed_at REAL,
        file_size INTEGER,               -- size+mtime fingerprint: an unchanged
        file_mtime REAL,                 --   file is skipped on re-sweep
        focus INTEGER DEFAULT 0          -- 1 = in the reading folder right now
        )""")
    # Older DBs predate these columns; add them rather than forcing a rebuild of
    # a corpus that may hold hundreds of books.
    have = {r[1] for r in conn.execute("PRAGMA table_info(books)")}
    for col, decl in (("file_size", "INTEGER"), ("file_mtime", "REAL"),
                      ("focus", "INTEGER DEFAULT 0")):
        if col not in have:
            conn.execute(f"ALTER TABLE books ADD COLUMN {col} {decl}")
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
        text, book_id UNINDEXED, pdf_page UNINDEXED, tokenize='porter')""")
    return conn


def _printed(pdf_page: int, offset: int) -> str:
    """Printed page label for a physical page.

    Front matter sits before printed p.1 and is usually numbered in roman
    numerals, which a single linear offset cannot express — it goes negative.
    Report those pages as front matter rather than printing 'p.-10'.
    """
    n = pdf_page - (offset or 0)
    return str(n) if n >= 1 else "front matter"


def _measure_offset(pages: list[tuple[int, str]]) -> tuple[int, int, int]:
    """Measure front-matter offset from the page numbers printed on the pages.

    Every book prints its own page number in the running head or foot, so the
    offset can be observed instead of guessed: for each page, any number in the
    first or last line is a candidate printed number, voting for
    `pdf_page - printed`. The true offset wins by a landslide because it is the
    only value that agrees across the whole book.

    This replaces inferring from the TOC, which fails on the many books whose
    outline lists only part names ("I Foundations") and never "Chapter 1".

    Returns (offset, winning_votes, pages_sampled) so callers can judge
    confidence; a weak margin means the book has no usable printed numbers.
    """
    votes: dict[int, int] = {}
    for pdf_page, text in pages:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            continue
        for cand in lines[:1] + lines[-1:]:
            for m in re.findall(r"\b(\d{1,4})\b", cand):
                printed = int(m)
                if 0 < printed <= pdf_page:          # printed number never exceeds physical
                    votes[pdf_page - printed] = votes.get(pdf_page - printed, 0) + 1
    if not votes:
        return 0, 0, len(pages)
    offset, count = max(votes.items(), key=lambda kv: kv[1])
    return offset, count, len(pages)


def _fts_query(raw: str) -> str:
    """Turn ordinary search words into a valid FTS5 query.

    Technical vocabulary is full of characters FTS5 treats as operators:
    'red-black tree' parses the hyphen as NOT and errors, 'C++' and 'std::vector'
    are syntax errors outright. Users should not have to know FTS5 grammar, so
    bare terms are quoted into literals.

    Deliberate operator use survives: a query already containing double quotes,
    or using uppercase AND/OR/NOT between terms, is passed through untouched.
    """
    if '"' in raw:
        return raw                                  # caller wrote their own phrase syntax
    tokens = raw.split()
    if any(t in ("AND", "OR", "NOT") for t in tokens):
        # Keep operators bare; quote the operands around them.
        return " ".join(t if t in ("AND", "OR", "NOT") else f'"{t}"'
                        for t in tokens if t.strip())
    return " ".join(f'"{t}"' for t in tokens if t.strip())


# ---------------------------------------------------------------- extraction

def _read_text_file(path: Path) -> str:
    """Read a text/markdown file, tolerating the encodings real files arrive in."""
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _split_text(body: str) -> list[str]:
    """Split a text document into page-sized chunks, preferring heading breaks.

    Markdown headings are the document's own structure, so a chunk that starts
    at a heading stays readable on its own. Long sections are split by size so
    one wall-of-text section cannot become a single unreadable chunk.
    """
    lines = body.splitlines()
    chunks: list[str] = []
    cur: list[str] = []
    size = 0
    for line in lines:
        is_heading = line.startswith("#") or (line.startswith("=") and len(line) > 3)
        # A heading starts a new chunk once the current one holds real content;
        # an over-long section splits on size even without a heading. Parenthesised
        # deliberately — `a and b or c` would bind as `(a and b) or c` and split
        # every heading regardless of size.
        start_new = (is_heading and size >= TEXT_CHUNK_CHARS // 10) or size >= TEXT_CHUNK_CHARS
        if cur and start_new:
            chunks.append("\n".join(cur))
            cur, size = [], 0
        cur.append(line)
        size += len(line) + 1
    if cur:
        chunks.append("\n".join(cur))
    return [c for c in chunks if c.strip()] or ([body] if body.strip() else [])


def _extract_text_doc(path: Path) -> dict:
    """Sweep one text/markdown document: headings become the TOC, chunks the pages."""
    body = _read_text_file(path)
    chunks = _split_text(body)

    # Every heading becomes a TOC entry, not just the first per chunk — a chunk
    # routinely holds several sections, and the ones after the first are exactly
    # what someone navigates to.
    toc = []
    for i, chunk in enumerate(chunks, start=1):
        for line in chunk.splitlines():
            if line.startswith("#"):
                toc.append({"title": line.lstrip("#").strip()[:120], "pdf_page": i})

    title = path.stem.replace("_", " ").replace("-", " ").strip()
    for line in body.splitlines():          # a leading H1 is the document's real title
        if line.startswith("# "):
            title = line.lstrip("#").strip()[:200]
            break

    return {
        "title": title,
        "author": "",
        "pages": len(chunks),
        "toc": toc,
        "page_offset": 0,                   # text chunks have no front matter to offset
        "text_quality": "ok" if body.strip() else "none",
    }


def _extract(path: Path) -> dict:
    """Sweep one PDF: metadata, page count, TOC, text-quality probe.

    Samples pages rather than reading all of them — the point of the sweep is
    that it stays cheap across hundreds of books.
    """
    reader = PdfReader(str(path))
    n = len(reader.pages)
    meta = reader.metadata or {}

    sample_idx = sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1} & set(range(n)))
    best = 0
    for i in sample_idx:
        try:
            best = max(best, len((reader.pages[i].extract_text() or "").strip()))
        except Exception:
            pass
    if best >= TEXT_OK_BEST_PAGE:
        quality = "ok"
    elif best >= TEXT_SPARSE_FLOOR:
        quality = "sparse"
    else:
        quality = "none"

    toc, offset = [], 0
    try:
        for item in reader.outline or []:
            if isinstance(item, list):
                continue
            try:
                p = reader.get_destination_page_number(item) + 1
                toc.append({"title": str(item.title).strip(), "pdf_page": p})
            except Exception:
                continue
    except Exception:
        pass

    # A provisional offset from the TOC: the first entry that looks like chapter
    # one. Weak — many books list only part names — so full_index() replaces it
    # with a measured value once real page text is available.
    for e in toc:
        if re.match(r"^(chapter\s+)?1\b|^introduction\b", e["title"], re.I):
            offset = e["pdf_page"] - 1
            break

    # PDF metadata is routinely blank or a generator's placeholder ("untitled",
    # the LaTeX job name). The filename is the more reliable title in practice,
    # so only trust /Title when it is substantive.
    raw_title = str(meta.get("/Title") or "").strip() if meta else ""
    if len(raw_title) < 3 or raw_title.lower() in {"untitled", "unknown", "document"}:
        raw_title = path.stem.replace("_", " ").replace("-", " ").strip()

    return {
        "title": raw_title,
        "author": str(meta.get("/Author") or "").strip() if meta else "",
        "pages": n,
        "toc": toc,
        "page_offset": offset,
        "text_quality": quality,
    }


# ---------------------------------------------------------------- tools

@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": True})
def ingest_book(path: str, force: bool = False) -> str:
    """Sweep one document into the corpus (metadata, TOC, text-quality probe only).

    Handles PDFs and text documents (.md, .txt, .rst) — books, specs, runbooks,
    any reference you would otherwise reread from disk each time. Use when
    adding a single file, before reading it. Cheap — does not extract full text;
    call full_index for that.

    Safe and fast to re-run: a file whose size and mtime are unchanged is
    skipped, so adding one document to a large corpus costs one file's work.
    Pass force=True to re-read a file the fingerprint says is unchanged.
    Returns the id, page/section count, and text quality.
    """
    p = Path(path).expanduser()
    if not p.is_file():
        return f"ERROR: no file at {p}. Pass an absolute path to a document file."
    if p.suffix.lower() not in BOOK_EXTS:
        return f"ERROR: unsupported type {p.suffix}. Supported: {', '.join(sorted(BOOK_EXTS))}"

    # An unchanged file is skipped outright: re-opening and re-sampling every
    # book to re-derive metadata that cannot have changed made adding one book
    # to a 160-book library cost a full re-sweep (~6 minutes).
    st = p.stat()
    if not force:
        with db() as c:
            prev = c.execute(
                "SELECT id,file_size,file_mtime,pages,text_quality FROM books WHERE path=?",
                (str(p),)).fetchone()
        if (prev and prev["file_size"] == st.st_size
                and prev["file_mtime"] == st.st_mtime):
            return (f"unchanged #{prev['id']}: {p.name} — {prev['pages']} pages, "
                    f"text_quality={prev['text_quality']} (skipped; pass force=True to re-read).")

    try:
        info = _extract(p) if p.suffix.lower() in PDF_EXTS else _extract_text_doc(p)
    except Exception as e:
        with db() as c:
            c.execute(
                """INSERT INTO books(path,title,text_quality,swept_at) VALUES(?,?,'error',?)
                   ON CONFLICT(path) DO UPDATE SET text_quality='error', swept_at=excluded.swept_at""",
                (str(p), p.stem, time.time()),
            )
        return f"ERROR: could not read {p.name}: {type(e).__name__}: {e}"

    with db() as c:
        c.execute(
            """INSERT INTO books(path,title,author,pages,page_offset,toc_json,text_quality,
                                 swept_at,file_size,file_mtime)
               VALUES(?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(path) DO UPDATE SET
                 title=excluded.title, author=excluded.author, pages=excluded.pages,
                 page_offset=excluded.page_offset, toc_json=excluded.toc_json,
                 text_quality=excluded.text_quality, swept_at=excluded.swept_at,
                 file_size=excluded.file_size, file_mtime=excluded.file_mtime""",
            (str(p), info["title"], info["author"], info["pages"], info["page_offset"],
             json.dumps(info["toc"]), info["text_quality"], time.time(),
             st.st_size, st.st_mtime),
        )
        bid = c.execute("SELECT id FROM books WHERE path=?", (str(p),)).fetchone()["id"]
        # The file changed (or we were forced), so any existing full-text index
        # describes the old content. Drop it rather than serve stale hits.
        stale = c.execute("SELECT COUNT(*) n FROM chunks WHERE book_id=?", (bid,)).fetchone()["n"]
        if stale:
            c.execute("DELETE FROM chunks WHERE book_id=?", (bid,))
            c.execute("UPDATE books SET full_indexed_at=NULL WHERE id=?", (bid,))

    warn = ""
    if stale:
        warn += (f"  NOTE: file changed since it was indexed; its {stale} stale chunks were "
                 f"dropped. Call full_index({bid}) to make the new content searchable.")
    if info["text_quality"] != "ok":
        warn += (f"  WARNING: text layer is '{info['text_quality']}' — likely scanned. "
                 f"Full-text search will not work; OCR it first.")
    return (f"swept #{bid}: {info['title']} — {info['pages']} pages, "
            f"{len(info['toc'])} TOC entries, text_quality={info['text_quality']}, "
            f"page_offset={info['page_offset']}.{warn}")


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": True})
def ingest_dir(path: str, recursive: bool = True, force: bool = False) -> str:
    """Sweep every document in a directory into the corpus (metadata only).

    Use to bring a whole library or docs folder in at once — PDFs and text
    documents (.md, .txt, .rst) alike. Cheap per file; no full text.

    Cheap to re-run after adding files: unchanged documents are skipped by a
    size+mtime check, so a re-sweep costs roughly the new files only. Pass
    force=True to re-read everything.
    Returns counts by text quality, how many were skipped, and any failures.
    """
    d = Path(path).expanduser()
    if not d.is_dir():
        return f"ERROR: not a directory: {d}. Pass an absolute path to a folder."
    files = [f for f in (d.rglob("*") if recursive else d.glob("*"))
             if f.suffix.lower() in BOOK_EXTS]
    if not files:
        return f"No {'/'.join(sorted(BOOK_EXTS))} files under {d}."

    tally: dict[str, int] = {}
    problems = []
    skipped = 0
    for f in files:
        res = ingest_book(str(f), force=force)
        if res.startswith("ERROR"):
            tally["error"] = tally.get("error", 0) + 1
            problems.append(f"  {f.name}: {res[7:]}")
        elif res.startswith("unchanged"):
            skipped += 1
        else:
            q = res.split("text_quality=")[1].split(",")[0]
            tally[q] = tally.get(q, 0) + 1
            if q != "ok":
                problems.append(f"  {f.name}: text_quality={q} (scanned? needs OCR)")

    processed = len(files) - skipped
    lines = [f"swept {len(files)} file(s) under {d}: {processed} read, {skipped} unchanged"]
    if tally:
        lines.append("  " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    if problems:
        lines.append(f"needs attention ({len(problems)}):")
        lines += problems[:20]
        if len(problems) > 20:
            lines.append(f"  ... and {len(problems) - 20} more")
    with db() as c:
        pend = c.execute("SELECT COUNT(*) n, COALESCE(SUM(pages),0) p FROM books "
                         "WHERE full_indexed_at IS NULL AND text_quality != 'none'").fetchone()
    if pend["n"]:
        lines.append(f"{pend['n']} document(s) hold metadata only and are NOT searchable. "
                     f"That is the intended resting state — index what you actually read: "
                     f"put it in the reading folder and call sync_focus(), or full_index(id) "
                     f"for one document.")
    return "\n".join(lines)


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": True})
def full_index(book_id: int) -> str:
    """Extract every page of one book into the searchable full-text index.

    Use before searching inside a book you are about to read; this is the
    expensive pass. Safe to re-run — replaces that book's existing chunks.
    Returns pages indexed, or refuses if the book has no usable text layer.
    """
    with db() as c:
        row = c.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not row:
        return f"ERROR: no book with id {book_id}. Call list_books() to see valid ids."
    if row["text_quality"] == "none":
        return (f"ERROR: '{row['title']}' has no text layer (scanned images). "
                f"Indexing it would produce searchable nothing. OCR it first, then re-sweep.")

    is_pdf = Path(row["path"]).suffix.lower() in PDF_EXTS
    try:
        pages = (list(PdfReader(row["path"]).pages) if is_pdf
                 else _split_text(_read_text_file(Path(row["path"]))))
    except Exception as e:
        return f"ERROR: cannot open {row['path']}: {type(e).__name__}: {e}"

    extracted: list[tuple[int, str]] = []
    with db() as c:
        c.execute("DELETE FROM chunks WHERE book_id=?", (book_id,))   # idempotent re-run
        n = 0
        for i, page in enumerate(pages, start=1):
            try:
                text = ((page.extract_text() or "") if is_pdf else page).strip()
            except Exception:
                continue
            if text:
                c.execute("INSERT INTO chunks(text,book_id,pdf_page) VALUES(?,?,?)",
                          (text, book_id, i))
                extracted.append((i, text))
                n += 1

        # Now that real page text exists, measure the front-matter offset instead
        # of trusting the TOC guess made at sweep time. Text documents have no
        # printed page numbers to measure, so their chunk index is the only
        # numbering and the offset stays 0.
        if is_pdf:
            offset, votes, sampled = _measure_offset(extracted)
            confident = sampled > 0 and votes >= max(10, 0.15 * sampled)
        else:
            offset, votes, sampled, confident = 0, 0, len(extracted), False
        # Either way the measurement is authoritative. A rejected measurement
        # must also CLEAR the provisional TOC guess: keeping it would leave every
        # printed-page number resting on an unverified inference while the tool
        # reports that measurement failed — wrong numbers, stated confidently.
        c.execute("UPDATE books SET page_offset=?, full_indexed_at=? WHERE id=?",
                  (offset if confident else 0, time.time(), book_id))

    unit = "pages" if is_pdf else "sections"
    note = ""
    if is_pdf and n < (row["pages"] or 0) * 0.5:
        note = (f"\n  WARNING: only {n} of {row['pages']} pages yielded text — "
                f"partial scan or heavy figures; search coverage is incomplete.")
    if not is_pdf:
        page_note = ("\n  text document: numbering is by section chunk, not printed pages.")
    elif confident:
        page_note = (f"\n  page offset measured at {offset} "
                     f"({votes}/{sampled} pages agree): printed p.1 is pdf p.{offset + 1}.")
    else:
        page_note = ("\n  page offset could not be measured (no consistent printed page "
                     "numbers); pdf and printed numbers are treated as identical.")
    return (f"indexed '{row['title']}': {n} of {row['pages']} {unit} searchable."
            f"{note}{page_note}")


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": True})
def sync_focus(path: str, budget_seconds: int = 240) -> str:
    """Make the reading folder the focus set: index what is in it, unfocus what left.

    Point this at the folder holding what you are actively reading. Documents in
    it are swept, full-indexed, and become the default scope for search_corpus.
    Documents that have left the folder stop being the default — but KEEP their
    text, so a book you finished stays searchable via scope="all".

    Nothing is ever un-indexed: reading a document promotes it permanently, and
    the corpus grows only with documents you actually opened. Safe to re-run;
    unchanged documents cost nothing. Stops cleanly at budget_seconds with
    progress saved. Returns what entered focus, what left, and what was indexed.
    """
    d = Path(path).expanduser()
    if not d.is_dir():
        return (f"ERROR: not a directory: {d}. Pass the folder holding what you are "
                f"reading, e.g. sync_focus('L:/books/reading').")

    on_disk = [f for f in d.rglob("*") if f.suffix.lower() in BOOK_EXTS]
    started = time.time()

    entered, indexed, failed, ran_out = [], [], [], False
    for f in on_disk:
        if budget_seconds and time.time() - started > budget_seconds:
            ran_out = True
            break
        res = ingest_book(str(f))
        if res.startswith("ERROR"):
            failed.append(f"  {f.name}: {res[7:90]}")
            continue
        with db() as c:
            row = c.execute("SELECT id,title,focus,full_indexed_at,text_quality "
                            "FROM books WHERE path=?", (str(f),)).fetchone()
        if not row:
            continue
        if not row["focus"]:
            entered.append(row["title"][:55])
        with db() as c:
            c.execute("UPDATE books SET focus=1 WHERE id=?", (row["id"],))
        if row["full_indexed_at"] is None and row["text_quality"] != "none":
            r = full_index(row["id"])
            (failed if r.startswith("ERROR") else indexed).append(
                f"  {row['title'][:55]}" + (f": {r[7:90]}" if r.startswith("ERROR") else ""))

    # Anything focused but no longer in the folder drops out of the default
    # scope. Its chunks stay: a finished book must remain searchable, or search
    # goes silent on a book you know you read.
    paths = {str(f) for f in on_disk}
    left = []
    with db() as c:
        for row in c.execute("SELECT id,title,path FROM books WHERE focus=1"):
            if row["path"] not in paths:
                c.execute("UPDATE books SET focus=0 WHERE id=?", (row["id"],))
                left.append(row["title"][:55])

    with db() as c:
        st = c.execute("""SELECT
            SUM(CASE WHEN focus=1 THEN 1 ELSE 0 END) focus,
            SUM(CASE WHEN focus=0 AND full_indexed_at IS NOT NULL THEN 1 ELSE 0 END) reference
            FROM books""").fetchone()

    lines = [f"focus folder: {d}  ({time.time() - started:.0f}s)"]
    if entered:
        lines.append(f"entered focus ({len(entered)}):")
        lines += [f"  {t}" for t in entered[:15]]
    if indexed:
        lines.append(f"newly indexed ({len(indexed)}):")
        lines += indexed[:15]
    if left:
        lines.append(f"left focus, still searchable via scope='all' ({len(left)}):")
        lines += [f"  {t}" for t in left[:15]]
    if failed:
        lines.append(f"failed ({len(failed)}):")
        lines += failed[:10]
    if ran_out:
        lines.append(f"stopped at the {budget_seconds}s budget — progress saved, "
                     f"call sync_focus again to continue.")
    if not (entered or indexed or left or failed):
        lines.append("no changes — focus set already matches the folder.")
    lines.append(f"now: {st['focus'] or 0} in focus, {st['reference'] or 0} reference "
                 f"(finished but searchable).")
    return "\n".join(lines)


@mcp.tool(annotations={"readOnlyHint": True})
def list_books(filter: str = "", limit: int = 30) -> str:
    """List documents in the corpus with their state, newest sweep first.

    Call this FIRST, before extracting or reading any document directly — one
    already in the corpus should be queried, not re-read. `filter` matches
    title, author, or path (case-insensitive).

    Each row is one of three states: `focus` (in the reading folder, searched by
    default), `reference` (finished but still searchable via scope='all'), or
    `swept` (metadata only, not searchable until full_index).
    """
    q = """SELECT b.*, (SELECT COUNT(*) FROM chunks WHERE book_id=b.id) AS n_chunks
           FROM books b"""
    args: list = []
    if filter:
        q += " WHERE lower(b.title) LIKE ? OR lower(b.author) LIKE ? OR lower(b.path) LIKE ?"
        args = [f"%{filter.lower()}%"] * 3
    q += " ORDER BY b.swept_at DESC LIMIT ?"
    args.append(max(1, min(limit, 200)))

    with db() as c:
        rows = c.execute(q, args).fetchall()
        total = c.execute("SELECT COUNT(*) AS n FROM books").fetchone()["n"]
    if not rows:
        return ("Corpus is empty. Call ingest_dir('/path/to/books') to sweep a library."
                if not filter else f"No books match '{filter}' (corpus holds {total}).")

    lines = [f"{len(rows)} of {total} document(s):"]
    for r in rows:
        if r["focus"]:
            state = f"focus ({r['n_chunks']}p indexed)"
        elif r["n_chunks"]:
            state = f"reference ({r['n_chunks']}p indexed)"
        else:
            state = "swept (not searchable)"
        flag = "" if r["text_quality"] == "ok" else f" [text:{r['text_quality']}]"
        lines.append(f"  #{r['id']} {r['title']} — {r['pages']}p, {state}{flag}")
    if total > len(rows):
        lines.append(f"  ... {total - len(rows)} more; narrow with filter= or raise limit=")
    return "\n".join(lines)


@mcp.tool(annotations={"readOnlyHint": True})
def search_corpus(query: str, limit: int = 10, book_id: int = 0,
                  scope: str = "focus") -> str:
    """Full-text search; defaults to what you are currently reading.

    scope="focus" (default) searches only documents in the reading folder, so
    hits come from the material actually in front of you rather than every book
    that happens to mention the word. scope="all" searches everything indexed,
    including documents you finished reading — use it for "which of my books
    cover X". Pass book_id to search within one document.

    Returns ranked snippets with page numbers: feed those to get_pages and read
    that span alone — never load a whole book to answer a question about one
    passage. Hyphenated and punctuated terms are handled automatically. Hits in
    a book's index pages look like keyword lists; prefer prose hits.
    """
    if not query.strip():
        return "ERROR: empty query. Pass search terms, e.g. search_corpus('consensus protocol')."
    if scope not in ("focus", "all"):
        return f"ERROR: scope must be 'focus' or 'all', got {scope!r}."
    fts_query = _fts_query(query)
    lim = max(1, min(limit, MAX_HITS))

    def run(sc: str) -> list:
        sql = """SELECT c.book_id, c.pdf_page, b.title, b.page_offset,
                        snippet(chunks, 0, '>>', '<<', ' … ', 12) AS snip
                 FROM chunks c JOIN books b ON b.id=c.book_id
                 WHERE chunks MATCH ?"""
        args: list = [fts_query]
        if sc == "focus":
            sql += " AND b.focus=1"
        if book_id:
            sql += " AND c.book_id=?"
            args.append(book_id)
        sql += " ORDER BY rank LIMIT ?"
        args.append(lim)
        with db() as c:
            return c.execute(sql, args).fetchall()

    try:
        rows = run(scope)
        with db() as c:
            counts = c.execute("""SELECT
                SUM(CASE WHEN focus=1 AND full_indexed_at IS NOT NULL THEN 1 ELSE 0 END) f,
                SUM(CASE WHEN full_indexed_at IS NOT NULL THEN 1 ELSE 0 END) a
                FROM books""").fetchone()
    except sqlite3.OperationalError as e:
        return (f"ERROR: could not run query {query!r}: {e}. Plain words and hyphenated "
                f"terms are handled automatically; if you wrote your own \"quoted phrase\" "
                f"or AND/OR/NOT operators, check they are balanced.")

    n_focus, n_all = counts["f"] or 0, counts["a"] or 0
    searched = n_focus if scope == "focus" else n_all

    if not rows:
        if not n_all:
            return ("Nothing is indexed yet. Put what you are reading in the reading "
                    "folder and call sync_focus('<that folder>'), or full_index(book_id) "
                    "for one document.")
        if scope == "focus":
            if not n_focus:
                return (f"Nothing is in focus, so a focus-scoped search has nothing to "
                        f"look at. {n_all} document(s) are indexed — retry with "
                        f"scope='all', or sync_focus() the reading folder.")
            # The whole point of the focus default is precision, so never let it
            # hide a real hit: say plainly that the wider corpus has one.
            if run("all"):
                return (f"No hits for {query!r} in the {n_focus} document(s) you are "
                        f"reading — but the wider corpus has hits. "
                        f"Retry with scope='all' to search all {n_all} indexed document(s).")
        return (f"No hits for {query!r} across {searched} indexed document(s) "
                f"(scope={scope}). This is not proof the topic is absent: only "
                f"full-indexed documents are searched (list_books shows which), keyword "
                f"search misses paraphrase, and a document flagged text_quality=none has "
                f"no searchable text at all.")

    where = (f"{searched} document(s) in focus" if scope == "focus"
             else f"all {searched} indexed document(s)")
    lines = [f"{len(rows)} hit(s) for {query!r} across {where}:"]
    for r in rows:
        snip = re.sub(r"\s+", " ", r["snip"])[:SNIPPET_CHARS]
        lines.append(f"  #{r['book_id']} {r['title']} — pdf p.{r['pdf_page']} "
                     f"(printed p.{_printed(r['pdf_page'], r['page_offset'])})")
        lines.append(f"      {snip}")
    lines.append("Next: get_pages(book_id, start, end) using the pdf page numbers above.")
    return "\n".join(lines)


@mcp.tool(annotations={"readOnlyHint": True})
def get_pages(book_id: int, start: int, end: int = 0, printed: bool = False) -> str:
    """Return the full text of one page span from an indexed book.

    Use after search_corpus to read the passage around a hit. Page numbers are
    pdf indexes by default; set printed=True to use the numbers printed on the
    paper. Span is capped at 20 pages. Returns the page text, page-labelled.
    """
    with db() as c:
        row = c.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            return f"ERROR: no book with id {book_id}. Call list_books() to see valid ids."
        off = row["page_offset"] or 0
        s = start + off if printed else start
        # end=0 means "just the start page". Resolve that BEFORE adding the
        # offset — offsetting a zero produces a bogus span reaching back into
        # the front matter.
        e = s if not end else (end + off if printed else end)
        if e < s:
            s, e = e, s
        if e - s + 1 > MAX_PAGE_SPAN:
            return (f"ERROR: span {s}-{e} exceeds the {MAX_PAGE_SPAN}-page cap. "
                    f"Request a narrower range, e.g. get_pages({book_id}, {s}, {s + MAX_PAGE_SPAN - 1}).")
        rows = c.execute(
            "SELECT pdf_page,text FROM chunks WHERE book_id=? AND pdf_page BETWEEN ? AND ? "
            "ORDER BY pdf_page", (book_id, s, e)).fetchall()

    if not rows:
        if not row["full_indexed_at"]:
            return (f"ERROR: '{row['title']}' has no full text indexed. "
                    f"Call full_index({book_id}) first.")
        return (f"No text on pdf pages {s}-{e} of '{row['title']}' "
                f"(blank, images, or beyond its {row['pages']} pages).")

    span = (f"printed {_printed(s, off)}" if s == e
            else f"printed {_printed(s, off)}–{_printed(e, off)}")
    out = [f"'{row['title']}' — pdf pages {s}-{e} ({span}):"]
    for r in rows:
        out.append(f"\n--- pdf p.{r['pdf_page']} (printed p.{_printed(r['pdf_page'], off)}) ---")
        out.append(r["text"])
    return "\n".join(out)


@mcp.tool(annotations={"readOnlyHint": True})
def get_toc(book_id: int) -> str:
    """Return one book's table of contents with page numbers.

    Use to orient in a book before reading, or to pick a section to load.
    Returns chapter/section titles with pdf and printed page numbers.
    """
    with db() as c:
        row = c.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not row:
        return f"ERROR: no book with id {book_id}. Call list_books() to see valid ids."
    toc = json.loads(row["toc_json"] or "[]")
    if not toc:
        return (f"'{row['title']}' has no embedded TOC ({row['pages']} pages). "
                f"Use search_corpus to locate topics instead.")
    off = row["page_offset"] or 0
    lines = [f"'{row['title']}' — {len(toc)} TOC entries (page_offset={off}):"]
    for e in toc:
        lines.append(f"  pdf p.{e['pdf_page']} (printed p.{_printed(e['pdf_page'], off)})  {e['title']}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
