---
name: sql-review
description: Review a SQL query for plan risks, index needs, and correctness traps. Use for "review this query", "why is this slow", "optimize this SQL", or any nontrivial query in a diff.
derivation: original
flow: review
---

# SQL Review

## Checks, in order
1. **Sargability:** predicates that defeat indexes — functions on columns (`WHERE date(created_at)=…`), leading-wildcard LIKE, implicit type casts, OR across different columns.
2. **Join shape:** join columns typed and indexed on both sides; row-count explosion from many-to-many joins before aggregation; accidental cross joins.
3. **Index fit:** does an index cover (filter columns → sort columns → selected columns)? Name the exact composite index that would serve the query, in column order.
4. **Pagination + N+1:** OFFSET-based pagination on large tables (recommend keyset); per-row subqueries or app-side loops that should be one query.
5. **Correctness traps:** NULL semantics in NOT IN / <> comparisons, GROUP BY columns vs selected columns, timezone handling on date boundaries, isolation assumptions for read-modify-write.
6. Recommend verifying with the engine's plan (`EXPLAIN (ANALYZE, BUFFERS)` / engine equivalent) — reasoning predicts, the plan confirms.

## Output
Findings ranked by expected impact, each with the concrete rewrite or index DDL. State the assumed engine; semantics differ (Postgres vs MySQL vs Oracle) and the review must say which rules applied.
