---
name: sqlite
description: Use SQLite from Python (stdlib sqlite3) correctly — parameterized queries, transactions, Row access, WAL, pragmas. Use for "store this locally", "quick database", "query this .db file", or any single-file persistence in a script or tool.
derivation: original
flow: util
---

# sqlite

Stdlib — no install.

## Safe shape

```python
import sqlite3

conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row                  # rows as dict-likes: row["name"]
conn.execute("PRAGMA foreign_keys = ON")        # OFF by default — enforce your FKs
conn.execute("PRAGMA journal_mode = WAL")       # readers don't block the writer

with conn:                                      # transaction: commits, or rolls back on exception
    conn.execute("INSERT INTO users(name, email) VALUES (?, ?)", (name, email))
    conn.executemany("INSERT INTO tags(uid, tag) VALUES (?, ?)", tag_rows)

rows = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
```

## The rules
- **Placeholders (`?`) always; never f-strings into SQL** — injection plus broken quoting on the first apostrophe. Identifiers (table/column names) can't be parameterized — whitelist them if dynamic.
- **Writes need a transaction boundary:** default mode buffers until `commit()`; scripts that "lose data" forgot it. `with conn:` handles commit/rollback.
- `executemany` for bulk — one statement, thousands of rows, orders of magnitude faster than a loop.

## Gotchas
- SQLite types are dynamic (type affinity): it will happily store `"abc"` in an INTEGER column. Validate in Python; add `CHECK` constraints for invariants.
- Datetimes: store ISO-8601 strings (`dt.isoformat()`) — the old implicit converters are deprecated; comparisons on ISO strings sort correctly.
- Concurrency: WAL allows many readers + one writer; a second writer gets `database is locked` — set `sqlite3.connect(..., timeout=10)` to wait instead of crash.
- `:memory:` databases vanish per-connection; share one connection if tests need shared state.
