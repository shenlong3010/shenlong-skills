#!/usr/bin/env python3
"""Smoke: sweep, text-quality gating, full-text search, page mapping, idempotence, caps.

Builds real PDFs with reportlab and runs the real tools against a temp DB — no
mocks. Run: python test_corpus.py
"""
import os
import sys
import tempfile
from pathlib import Path

TMP = Path(tempfile.gettempdir()) / "book-corpus-test"
TMP.mkdir(exist_ok=True)
os.environ["BOOK_CORPUS_DB"] = str(TMP / "test.db")
Path(os.environ["BOOK_CORPUS_DB"]).unlink(missing_ok=True)

sys.path.insert(0, str(Path(__file__).parent))
import server as S  # noqa: E402  (after env var — DB_PATH is read at import)

S.DB_PATH = Path(os.environ["BOOK_CORPUS_DB"])

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("needs reportlab: pip install reportlab  (or: uvx --with reportlab --with pypdf --with fastmcp python test_corpus.py)")


FILLER = ("Prose filler so each page carries realistic density; a real book page "
          "holds a few thousand characters, not one line. ")


def make_pdf(path: Path, pages: list[str], dense: bool = True) -> Path:
    """Write a PDF, one page per string, padded to book-like text density."""
    c = canvas.Canvas(str(path), pagesize=letter)
    for body in pages:
        c.drawString(72, 720, body)
        if dense:
            y = 700
            for i in range(12):
                c.drawString(72, y, f"{FILLER}line {i}")
                y -= 14
        c.showPage()
    c.save()
    return path


def make_image_pdf(path: Path, n: int = 3) -> Path:
    """A PDF with no text layer — a rectangle per page, standing in for a scan."""
    c = canvas.Canvas(str(path), pagesize=letter)
    for _ in range(n):
        c.rect(100, 400, 300, 200, fill=1)
        c.showPage()
    c.save()
    return path


def main() -> None:
    books = TMP / "books"
    books.mkdir(exist_ok=True)
    for f in books.glob("*.pdf"):
        f.unlink()

    # A findable phrase on a known page: page 3 of 5.
    make_pdf(books / "distributed.pdf", [
        "Front matter and copyright",
        "Table of contents",
        "The Raft consensus protocol elects a single leader per term.",
        "Log replication follows the leader election phase.",
        "Index and colophon",
    ])
    make_pdf(books / "networks.pdf", ["Packet switching basics", "Congestion control windows"])
    make_image_pdf(books / "scanned.pdf")
    # Thin text everywhere — a page-number-only scan. Should read 'sparse', the
    # middle verdict: text exists but is too thin to trust as a real layer.
    make_pdf(books / "thin.pdf", ["7", "8", "9"], dense=False)

    # --- sweep -----------------------------------------------------------
    out = S.ingest_dir(str(books))
    print(out)
    assert "swept 4 file(s)" in out, "expected 4 files swept"
    # Three-way verdict: real text / thin text / no text layer at all.
    assert "ok=2" in out, f"expected 2 good-text books, got: {out}"
    assert "sparse=1" in out, f"expected the thin-text book flagged sparse, got: {out}"
    assert "none=1" in out, f"expected the image-only book flagged none, got: {out}"

    listing = S.list_books()
    print(listing)
    assert "distributed" in listing.lower(), "swept book missing from listing"

    # --- scanned book is flagged, not silently indexed --------------------
    with S.db() as c:
        scanned = c.execute(
            "SELECT id,text_quality FROM books WHERE path LIKE '%scanned%'").fetchone()
    assert scanned["text_quality"] == "none", \
        f"image-only PDF should be text_quality=none, got {scanned['text_quality']}"
    refused = S.full_index(scanned["id"])
    print(refused)
    assert refused.startswith("ERROR") and "no text layer" in refused, \
        "indexing a scanned book must be refused, not silently produce an empty index"

    # --- full index + search ---------------------------------------------
    with S.db() as c:
        bid = c.execute("SELECT id FROM books WHERE path LIKE '%distributed%'").fetchone()["id"]
    print(S.full_index(bid))

    hits = S.search_corpus("Raft consensus")
    print(hits)
    assert "distributed" in hits.lower(), "known phrase did not return its book"
    assert "pdf p.3" in hits, f"phrase is on pdf page 3; got:\n{hits}"

    # --- searching an unindexed book returns guidance, not a lie ----------
    with S.db() as c:
        nid = c.execute("SELECT id FROM books WHERE path LIKE '%networks%'").fetchone()["id"]
    miss = S.search_corpus("congestion", book_id=nid)
    print(miss)
    assert "No hits" in miss, "unindexed book should yield no hits, not fabricated ones"

    # --- get_pages returns the page the phrase is actually on -------------
    page = S.get_pages(bid, 3)
    print(page[:200])
    assert "Raft consensus" in page, "get_pages(3) must return the page holding the phrase"

    # --- hyphenated / punctuated terms are not FTS syntax errors ----------
    # Regression: 'red-black tree' failed on a real book — FTS5 read the hyphen
    # as NOT. Technical vocabulary is full of these; users should not need to
    # know FTS5 grammar.
    assert S._fts_query("red-black tree") == '"red-black" "tree"'
    assert S._fts_query('"exact phrase"') == '"exact phrase"', "explicit phrases pass through"
    assert S._fts_query("a OR b") == '"a" OR "b"', "operators survive, operands get quoted"
    hyphen = S.search_corpus("leader-election OR consensus", book_id=bid)
    assert not hyphen.startswith("ERROR"), f"hyphenated query must not error: {hyphen}"

    # --- measured page offset ---------------------------------------------
    # Regression: offset was inferred from the TOC and silently wrong (0 instead
    # of 21) on a book whose outline lists only part names. It is now measured
    # from the numbers printed on the pages themselves.
    numbered = [(i, f"Chapter text for page {i - 4}\nbody line\n{i - 4}") for i in range(5, 40)]
    off, votes, sampled = S._measure_offset(numbered)
    assert off == 4, f"offset should measure 4 from printed numbers, got {off} ({votes}/{sampled})"
    assert votes >= 30, f"a consistent book should vote overwhelmingly, got {votes}"
    assert S._measure_offset([(1, "no numbers here"), (2, "none either")])[1] <= 1, \
        "unnumbered pages must not produce a confident offset"

    # A rejected measurement must CLEAR the provisional TOC guess, not defer to
    # it. Regression: a real book kept a TOC-inferred offset of 17 while
    # full_index reported measurement had failed, so every printed page number
    # rested on an unverified guess the tool had just disclaimed.
    with S.db() as c:
        c.execute("UPDATE books SET page_offset=99 WHERE id=?", (nid,))   # fake TOC guess
    S.full_index(nid)                       # 2 pages, no printed numbers -> not confident
    with S.db() as c:
        left = c.execute("SELECT page_offset FROM books WHERE id=?", (nid,)).fetchone()
    assert left["page_offset"] == 0, \
        f"unmeasurable offset must reset to 0, not keep the guess ({left['page_offset']})"

    # Front matter precedes printed p.1; a linear offset would report negatives.
    assert S._printed(3, 10) == "front matter", "pre-p.1 pages must not render as negative"
    assert S._printed(30, 10) == "20"

    # --- printed-page addressing with end omitted -------------------------
    # Regression: end=0 meant "just this page", but the offset was added to the
    # zero, producing a span reaching back into the front matter.
    with S.db() as c:
        c.execute("UPDATE books SET page_offset=2 WHERE id=?", (bid,))
    one = S.get_pages(bid, 1, printed=True)
    assert "pdf pages 3-3" in one, f"printed p.1 with offset 2 must be pdf p.3 alone: {one[:120]}"
    with S.db() as c:
        c.execute("UPDATE books SET page_offset=0 WHERE id=?", (bid,))

    # --- span cap ---------------------------------------------------------
    capped = S.get_pages(bid, 1, 999)
    assert capped.startswith("ERROR") and "cap" in capped, "oversized span must be refused"
    print(capped)

    # --- bad ids and empty queries are actionable errors ------------------
    assert S.get_pages(99999, 1).startswith("ERROR"), "unknown book id must error"
    assert S.search_corpus("").startswith("ERROR"), "empty query must error"

    # --- idempotence ------------------------------------------------------
    with S.db() as c:
        before = c.execute("SELECT COUNT(*) n FROM chunks WHERE book_id=?", (bid,)).fetchone()["n"]
    S.ingest_dir(str(books))
    S.full_index(bid)
    with S.db() as c:
        after = c.execute("SELECT COUNT(*) n FROM chunks WHERE book_id=?", (bid,)).fetchone()["n"]
        nbooks = c.execute("SELECT COUNT(*) n FROM books").fetchone()["n"]
    assert before == after, f"re-index duplicated chunks: {before} -> {after}"
    assert nbooks == 4, f"re-sweep duplicated books: {nbooks}"

    print("\nOK — sweep, quality gating, search, page mapping, caps, idempotence all pass.")


if __name__ == "__main__":
    main()
