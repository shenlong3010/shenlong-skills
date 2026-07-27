# Pass criteria — talk-notes-standard-year-precision

Real video (Awesome channel, "Postgres is dropping a crazy new feature", `zPsr0n9DQ7o`). Unlike
the jargon cases in this suite, nothing here is *garbled* — every proper noun is spelled and
pronounced correctly. The error is a **wrong fact attached to correctly-named things**: the
video says the ISO committee "formalized" both GQL and SQL/PGQ "back in 2023." Two related but
distinct standards, and only one of those dates is right.

Ground truth (verifiable against the ISO standards' own publication record, not journalism):

- **SQL/PGQ** is Part 16 of **SQL:2023**, published **June 2023** — the video's date is correct
  for this one.
- **GQL** (the standalone graph query language, ISO/IEC 39075) was published in **2024**, not
  2023 — the video's date is wrong for this one.

Everything else in the video's standards/feature discussion checks out and must not be
"corrected": PostgreSQL 19 Beta introducing SQL/PGQ, the `GRAPH_TABLE` function, property graphs
as read-only views over relational tables, fixed-depth-only pattern matching in this release
(no variable-length paths yet), September GA target, Oracle 23ai as the first commercial
SQL/PGQ implementation, Neo4j's index-free adjacency, and the ICIJ Panama Papers tool stack
(Neo4j, Apache Tika, Tesseract, Apache Solr, Blacklight).

1. **GQL's year corrected or flagged**: the notes must not repeat "GQL was formalized in 2023"
   as fact. PASS if EITHER the year is corrected to 2024 with a source in the Verification log,
   OR the claim is explicitly flagged as unverified/uncertain. Silently repeating the video's
   grouping of both standards under 2023 is a FAIL — this is the single criterion this case
   exists to test.
2. **SQL/PGQ's 2023 date NOT flagged as wrong**: this half of the claim is accurate. Marking it
   "corrected" or "unresolved" is a false positive and a FAIL. The failure mode this guards
   against is over-correction — noticing one date is wrong and reflexively distrusting the
   adjacent one.
3. **Postgres 19 feature claims confirmed, not flagged**: the SQL/PGQ feature description
   (GRAPH_TABLE, read-only views, fixed-depth-only limitation, September GA) is accurate and
   independently confirmable against PostgreSQL's own documentation and release notes. Flagging
   any of it as unverified when Context7/official docs confirm it is a FAIL.
4. **Verification log present and covers the standards claims**: entries required for GQL,
   SQL/PGQ, and at minimum the Postgres 19 feature claim — term, source consulted, tries,
   outcome. A correct-by-luck output with no log is not a pass, same law as every other case in
   this suite.

A PASS requires all four. This case is distinct from the garbled-name cases: it tests whether
the fact-check step (Method step 5) catches a **precise factual error on a correctly-named
entity** — the kind of error no spelling-based scan can find, and the kind most likely to be
repeated confidently because everything around it is right.
