#!/usr/bin/env python3
"""Inspect the book-corpus SQLite index — read-only, never writes.

The corpus is ONE `books` table (entities) plus ONE `chunks` FTS5 table (their
text). PDFs from the reading folder and any ingested markdown share both — there
is no separate table per content type, which is what lets one query rank a book
against a blog note.

Usage:
  python tools/corpus-inspect.py                    # summary: counts, dirs, focus
  python tools/corpus-inspect.py schema             # table DDL + columns
  python tools/corpus-inspect.py books              # every row, one line each
  python tools/corpus-inspect.py books --indexed    # only full-indexed rows
  python tools/corpus-inspect.py books --md         # only markdown (notes)
  python tools/corpus-inspect.py dirs               # source dirs by count
  python tools/corpus-inspect.py focus              # focus set + disk state
  python tools/corpus-inspect.py doctor             # dead paths, dupes, empty indexes
  python tools/corpus-inspect.py search mvcc        # FTS query (focus-scoped)
  python tools/corpus-inspect.py search "value separation" --phrase --all
  python tools/corpus-inspect.py toc 164            # one book's TOC
  python tools/corpus-inspect.py page 164 285       # print one chunk

Env:
  BOOK_CORPUS_DB   override index path (default ~/.local/share/book-corpus.db)

Exit codes: 0 clean · 1 findings (doctor problems / no search hits) · 2 usage error.
"""
import argparse
import collections
import json
import os
import pathlib
import sqlite3
import sys
import textwrap

DEFAULT_DB = pathlib.Path.home() / ".local" / "share" / "book-corpus.db"
NOTE_EXTS = (".md", ".markdown", ".txt", ".rst")
FTS_SPECIAL = set('"()*:^')


def connect(path):
    """Read-only connection: mode=ro means a bug here cannot corrupt the index."""
    if not path.exists():
        print(f"ERROR: no corpus index at {path}", file=sys.stderr)
        print("       set BOOK_CORPUS_DB, or ingest something first.", file=sys.stderr)
        raise SystemExit(2)
    uri = "file:" + path.resolve().as_posix() + "?mode=ro"
    c = sqlite3.connect(uri, uri=True)
    c.row_factory = sqlite3.Row
    return c


def kind_of(path):
    return "note" if path.lower().endswith(NOTE_EXTS) else "book"


def cmd_summary(c, args):
    n_books = c.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    n_chunks = c.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    n_idx = c.execute("SELECT COUNT(*) FROM books WHERE full_indexed_at IS NOT NULL").fetchone()[0]
    n_focus = c.execute("SELECT COUNT(*) FROM books WHERE focus=1").fetchone()[0]
    kinds = collections.Counter(kind_of(r["path"]) for r in c.execute("SELECT path FROM books"))

    print(f"index      {args.db}  ({args.db.stat().st_size // 1024 // 1024} MB)")
    print(f"books      {n_books} rows  ({kinds.get('book', 0)} documents, "
          f"{kinds.get('note', 0)} notes)")
    print(f"indexed    {n_idx} full-indexed -> {n_chunks} searchable chunks")
    print(f"focus      {n_focus} in the reading folder (default search scope)")
    print("\nONE books table + ONE chunks FTS index -- no per-type tables.")
    print("That is what lets a single query rank a document against a note.")

    qual = collections.Counter(r["text_quality"] or "?"
                               for r in c.execute("SELECT text_quality FROM books"))
    print("\ntext quality  " + "  ".join(f"{k}={v}" for k, v in sorted(qual.items())))

    print("\ntop source dirs:")
    dirs = collections.Counter(str(pathlib.PurePath(r["path"]).parent)
                               for r in c.execute("SELECT path FROM books"))
    for d, n in dirs.most_common(8):
        print(f"  {n:>4}  {d}")
    return 0


def cmd_schema(c, args):
    for r in c.execute("SELECT name, type, sql FROM sqlite_master "
                       "WHERE sql IS NOT NULL ORDER BY name"):
        print(f"--- {r['name']} ({r['type']}) ---")
        print(r["sql"])
        print()
    print("--- books columns ---")
    for d in c.execute("PRAGMA table_info(books)"):
        print(f"  {d['name']:<18} {d['type'] or 'ANY'}")
    print("\nNote: no `kind`/`source` column exists. A note and a book are told "
          "apart\nonly by file extension, which is a convention, not schema.")
    return 0


def cmd_books(c, args):
    rows = c.execute("""SELECT id, title, path, pages, text_quality, focus,
                        full_indexed_at IS NOT NULL AS idx
                        FROM books ORDER BY id""").fetchall()
    if args.indexed:
        rows = [r for r in rows if r["idx"]]
    if args.md:
        rows = [r for r in rows if kind_of(r["path"]) == "note"]
    if args.focus:
        rows = [r for r in rows if r["focus"]]

    print(f"{'id':>4} {'kind':<5} {'foc':>3} {'idx':<4} {'pg':>5} "
          f"{'qual':<7} {'disk':<8} title")
    print("-" * 98)
    for r in rows:
        on_disk = "ok" if pathlib.Path(r["path"]).exists() else "MISSING"
        title = (r["title"] or pathlib.PurePath(r["path"]).stem)[:42]
        print(f"{r['id']:>4} {kind_of(r['path']):<5} {r['focus'] or 0:>3} "
              f"{'yes' if r['idx'] else '-':<4} {r['pages'] or 0:>5} "
              f"{(r['text_quality'] or '?'):<7} {on_disk:<8} {title}")
    print(f"\n{len(rows)} row(s)")
    return 0


def cmd_dirs(c, args):
    dirs = collections.Counter(str(pathlib.PurePath(r["path"]).parent)
                               for r in c.execute("SELECT path FROM books"))
    for d, n in dirs.most_common():
        flag = "" if pathlib.Path(d).exists() else "   <- MISSING ON DISK"
        print(f"{n:>4}  {d}{flag}")
    return 0


def cmd_focus(c, args):
    rows = c.execute("""SELECT id, title, path, full_indexed_at IS NOT NULL AS idx
                        FROM books WHERE focus=1 ORDER BY id""").fetchall()
    if not rows:
        print("nothing in focus. sync_focus(<reading folder>) promotes what is in it.")
        return 0
    print("FOCUS SET (default scope for search):")
    for r in rows:
        flag = "" if pathlib.Path(r["path"]).exists() else "   <- MISSING ON DISK"
        print(f"  id={r['id']:<4} indexed={'yes' if r['idx'] else 'no':<4} "
              f"{(r['title'] or '?')[:54]}{flag}")
        print(f"          {r['path']}")
    ref = c.execute("""SELECT COUNT(*) FROM books WHERE (focus IS NULL OR focus=0)
                       AND full_indexed_at IS NOT NULL""").fetchone()[0]
    print(f"\n{ref} indexed row(s) out of focus -- still searchable with --all.")
    return 0


def cmd_doctor(c, args):
    """Report problems only. Exit 1 if any found."""
    problems = 0

    dead = [r for r in c.execute("SELECT id, title, path FROM books")
            if not pathlib.Path(r["path"]).exists()]
    if dead:
        problems += len(dead)
        print(f"DEAD PATHS ({len(dead)}) -- row points at a file that is gone.")
        print("  Text stays searchable by design; only re-index and page reads break.")
        for r in dead:
            print(f"  id={r['id']:<4} {(r['title'] or '?')[:46]:<46} {r['path'][:64]}")
        print()

    by_name = collections.defaultdict(list)
    for r in c.execute("SELECT id, title, path FROM books"):
        by_name[pathlib.PurePath(r["path"]).name.lower()].append(r)
    dupes = {k: v for k, v in by_name.items() if len(v) > 1}
    if dupes:
        problems += sum(len(v) - 1 for v in dupes.values())
        print(f"DUPLICATE FILENAMES ({len(dupes)} name(s) at >1 path)")
        print("  `path` is UNIQUE and there is no content dedup, so one document")
        print("  ingested from two folders is two rows and doubled search hits.")
        for name, rows in sorted(dupes.items()):
            print(f"  {name[:70]}")
            for r in rows:
                mark = "" if pathlib.Path(r["path"]).exists() else "  (missing)"
                print(f"      id={r['id']:<4} {r['path'][:70]}{mark}")
        print()

    empty = c.execute("""SELECT id, title FROM books WHERE full_indexed_at IS NOT NULL
                         AND id NOT IN (SELECT DISTINCT book_id FROM chunks)""").fetchall()
    if empty:
        problems += len(empty)
        print(f"INDEXED BUT NO CHUNKS ({len(empty)}) -- claims indexed, nothing searchable.")
        for r in empty:
            print(f"  id={r['id']:<4} {(r['title'] or '?')[:58]}")
        print()

    noq = c.execute("SELECT COUNT(*) FROM books "
                    "WHERE text_quality IN ('none','error')").fetchone()[0]
    if noq:
        print(f"note: {noq} row(s) with text_quality none/error -- scanned images, "
              f"not indexable without OCR.\n")

    if not problems:
        print("corpus clean: no dead paths, no duplicate filenames, no empty indexes.")
        return 0
    print(f"{problems} problem(s) found. Nothing was modified -- this tool is read-only.")
    return 1


def cmd_search(c, args):
    q = f'"{args.query}"' if args.phrase else args.query
    if not args.phrase and " " in args.query and not FTS_SPECIAL & set(args.query):
        print("note: multi-word queries are loose with the porter tokenizer --")
        print('      "value separation" matched "separate" in unrelated books.')
        print("      use --phrase for an exact match.\n")
    sql = """SELECT b.id, b.title, b.path, ch.pdf_page,
                    snippet(chunks, 0, '[', ']', ' ... ', 18) AS snip,
                    bm25(chunks) AS rank
             FROM chunks ch JOIN books b ON b.id = ch.book_id
             WHERE chunks MATCH ?"""
    params = [q]
    if not args.all:
        sql += " AND b.focus = 1"
    sql += " ORDER BY rank LIMIT ?"
    params.append(args.limit)
    try:
        rows = c.execute(sql, params).fetchall()
    except sqlite3.OperationalError as e:
        print(f"ERROR: bad FTS query: {e}", file=sys.stderr)
        return 2
    if not rows:
        where = "whole corpus" if args.all else "focus set (add --all to widen)"
        print(f"no hits for {args.query!r} in {where}.")
        return 1
    for r in rows:
        print(f"[{kind_of(r['path'])}] id={r['id']} §{r['pdf_page']}  "
              f"bm25={r['rank']:.1f}  {(r['title'] or '?')[:50]}")
        print(textwrap.fill(" ".join(r["snip"].split()), 78,
                            initial_indent="      ", subsequent_indent="      "))
        print()
    tail = "" if args.all else "  (focus-scoped; --all searches everything)"
    print(f"{len(rows)} hit(s).{tail}")
    return 0


def cmd_toc(c, args):
    r = c.execute("SELECT title, path, toc_json, pages, page_offset "
                  "FROM books WHERE id=?", (args.book_id,)).fetchone()
    if not r:
        print(f"no book id={args.book_id}", file=sys.stderr)
        return 2
    print(f"{r['title']}\n{r['path']}")
    print(f"pages={r['pages']} page_offset={r['page_offset']} "
          f"(printed = pdf_page - page_offset)\n")
    try:
        toc = json.loads(r["toc_json"] or "[]")
    except json.JSONDecodeError:
        print("(toc_json unparseable)")
        return 1
    if not toc:
        print("(no TOC recorded)")
        return 0
    for e in toc:
        if isinstance(e, dict):
            lvl = e.get("level", 1)
            print(f"  p.{str(e.get('page', '?')):>5}  "
                  f"{'  ' * max(0, lvl - 1)}{str(e.get('title', '?'))[:62]}")
        else:
            print(f"  {e}")
    return 0


def cmd_page(c, args):
    rows = c.execute("SELECT pdf_page, text FROM chunks WHERE book_id=? AND pdf_page=?",
                     (args.book_id, args.page)).fetchall()
    if not rows:
        print(f"no chunk for book {args.book_id} at §{args.page}", file=sys.stderr)
        return 1
    for r in rows:
        print(f"--- book {args.book_id} §{r['pdf_page']} ---")
        print(r["text"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Read-only inspector for the book-corpus SQLite index.")
    ap.add_argument("--db", type=pathlib.Path,
                    default=pathlib.Path(os.environ.get("BOOK_CORPUS_DB", DEFAULT_DB)),
                    help="index path (default $BOOK_CORPUS_DB or "
                         "~/.local/share/book-corpus.db)")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("summary", help="counts, source dirs, focus (default)")
    sub.add_parser("schema", help="table DDL and columns")
    b = sub.add_parser("books", help="one line per row")
    b.add_argument("--indexed", action="store_true", help="only full-indexed")
    b.add_argument("--md", action="store_true", help="only markdown notes")
    b.add_argument("--focus", action="store_true", help="only the focus set")
    sub.add_parser("dirs", help="source directories by count")
    sub.add_parser("focus", help="focus set and its disk state")
    sub.add_parser("doctor", help="dead paths, dupes, empty indexes (exit 1 if any)")
    s = sub.add_parser("search", help="FTS5 query")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--all", action="store_true", help="search everything, not just focus")
    s.add_argument("--phrase", action="store_true", help="exact phrase match")
    t = sub.add_parser("toc", help="a book's table of contents")
    t.add_argument("book_id", type=int)
    g = sub.add_parser("page", help="print one chunk's text")
    g.add_argument("book_id", type=int)
    g.add_argument("page", type=int)

    args = ap.parse_args(argv)
    handler = {None: cmd_summary, "summary": cmd_summary, "schema": cmd_schema,
               "books": cmd_books, "dirs": cmd_dirs, "focus": cmd_focus,
               "doctor": cmd_doctor, "search": cmd_search, "toc": cmd_toc,
               "page": cmd_page}[args.cmd]
    c = connect(args.db)
    try:
        return handler(c, args)
    finally:
        c.close()


if __name__ == "__main__":
    sys.exit(main())
