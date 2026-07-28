# Degraded twin — status listed, never reconciled

Fails criterion 2. Passes 1, 3, 4, 5.

The status section is correct and complete: merges and partition reassignments are explicitly
listed as unimplemented in the 25.2 preview. The architecture section, forty lines earlier, still
presents accuracy-over-many-cycles as an established property. Both statements are true; they
never meet, so the reader can still walk away believing the durability claim was measured. This
is the realistic version of the defect.

---

# C-SPANN: Real-Time Indexing for Billions of Vectors with CockroachDB

**Source:** https://www.cockroachlabs.com/blog/cspann-real-time-indexing-billions-vectors/ ·
published 23 June 2025

## Problem

Semantic search over user-generated content at billions-scale — millions of users each holding
hundreds to thousands of items, expecting results instantly and expecting them fresh. Existing
vector solutions assume the dataset fits in memory on one machine or on a fast local SSD; they do
not expect data distributed across regions, constantly changing, or part of a transactional
system, and they pay for it with batched writes, stale results, and specialized hardware.

An index is required because embeddings have hundreds or thousands of dimensions with no natural
ordering — should beach photos come before or after food photos? — so traditional indexes do not
apply, and brute force stops being practical past tens of thousands of vectors.

## The six constraints

No central coordinator; no large in-memory structures, state in persistent storage (called
especially important for Serverless); minimal network hops; a sharding-compatible layout mapping
onto KV ranges; no hot spots; incremental updates without blocking, rebuilds, or quality loss.
These "ruled out many common approaches."

## Architecture

C-SPANN is "CockroachDB SPANN," drawing on Microsoft's SPANN and SPFresh papers and Google's
ScaNN.

**Hierarchical k-means tree.** Vectors group into partitions of dozens to hundreds by similarity,
each with a centroid — the mean of its members. Centroids cluster recursively upward. From the
tree figure: each partition node holds a fixed-width slot array of child partition IDs beside its
centroid, uniform at every level, and only leaf partitions hold actual vectors. Slot arrays are
drawn partially filled, and that headroom is what split and merge work against.

**Storage mapping.** Each partition is a self-contained unit in the KV layer — a contiguous set of
key-value rows within a range — so ranges split, merge, and rebalance like any other table data.
The partitions/nodes figure shows containment as node ⊃ range ⊃ partitions and explicitly not one
partition per range: Node 2 holds two ranges, and Range 2 co-locates Partition 1 (the root) with
Partition 2, so tree level does not determine range placement.

**Query path.** Descend from the root comparing against each level's centroids, then scan
candidates at the leaves. Levels are processed in parallel, and because a partition's vectors are
packed and similar, SIMD scans blocks efficiently. Fanout around 100 keeps the tree wide and
shallow — 1M vectors in 3 levels, 10B in 5. Partition rows are cached by the storage layer's block
cache, with no specialized vector caching and no startup rebuild.

## Index maintenance

**Splits** run automatically in the background, dividing vectors into two roughly equal groups via
a balanced variant of k-means. The split figure shows the parent's own centroid being recomputed —
(0.5, 5.5) → (1.3, 4.7) — propagating upward to the root, so a leaf split is not just a slot-list
edit.

Partition splits are not range splits: a logical unit grouping similar vectors versus a physical
unit balancing storage and access. Adding nodes redistributes ranges at near-linear rates.

**Relocation after a split**, from SPFresh: a boundary vector may sit closer to a neighbouring
partition's centroid than to either new one, and vice versa. The relocation figure shows the
exchange is bidirectional. This is SPFresh's nearest partition assignment.

**Merges** reassign vectors and remove undersized partitions. The net claim is that accuracy holds
even after many cycles — start with an empty table, insert millions of vectors, and still get high
accuracy.

## Quantization

An OpenAI embedding is 1,536 dimensions of 2-byte floats, roughly 3 KB, and the bigger cost is the
CPU and memory to scan full vectors rather than storage. RaBitQ reduces each dimension to a single
bit — about 94%, roughly 3 KB down to 200 bytes. Quantization is relative to the partition's
centroid, so splits and merges only re-quantize the affected partition instead of forcing a global
retrain.

Four steps: random orthogonal transform (spreads skew, preserves angles and distances);
mean-centering on the partition centroid; normalization to unit length; each dimension to a bit,
zero if negative, one otherwise. The RaBitQ figure shows why step one matters — the original
100-dimension vector trends upward and is nearly all positive, so a sign bit would carry almost no
information; after the transform the values are symmetric noise about zero, roughly -8 to +7,
producing the balanced bit string sign encoding needs.

Stored per vector: the bit string, the dot product between quantized and original vectors, and the
exact distance from the centroid. Query vectors use a different asymmetric encoding at 4 bits per
dimension, SIMD-optimized. A reranking step fetches the original full vectors to recompute exact
distances, over-fetching to compensate, with RaBitQ's error bounds setting how many extras are
needed.

## Per-owner indexes and multi-region

Most queries are scoped to one owner, and including other users' vectors "could be a security
issue." Prefix columns partition the index by ownership:

```sql
CREATE TABLE photos (
  id UUID PRIMARY KEY,
  user_id UUID,
  embedding VECTOR(1536),
  VECTOR INDEX (user_id, embedding)
);
```

```sql
SELECT id
FROM photos
WHERE user_id = $1
ORDER BY embedding <-> $2
LIMIT 10
```

`<->` is pgvector-compatible. Performance is proportional to the vectors owned by that user, not
the total, because the index maintains a separate k-means tree per distinct user — "there isn't
much difference between 1 billion vectors in a single tree or the same number spread across a
million smaller trees."

Composing with multi-region (this block sits behind a JS "Show code" toggle and is absent from the
static HTML):

```sql
CREATE TABLE photos (
  id UUID PRIMARY KEY,
  user_id UUID,
  embedding VECTOR(1536),
  VECTOR INDEX (crdb_region, user_id, embedding)
) LOCALITY REGIONAL BY ROW;
```

`crdb_region` is added automatically and joins the index columns, co-locating table and index rows
per region — latency plus data domiciling.

## Status

Preview in 25.2. **Not yet implemented: merge operations and partition reassignments**, root
partition caching, expanded SIMD, and contention minimization. Planned: `IMPORT`, `ALTER INDEX`,
wider `WHERE` filter patterns, and cosine plus inner-product metrics — **Euclidean distance is the
only metric supported today**.

## What the post omits

No performance numbers at all — no QPS, latency percentiles, recall, or build times. "Near-linear"
and "high accuracy" are asserted, and the 94% is an algorithmic property for common cases rather
than a measurement on their workload. No named comparison: "ruled out many common approaches"
without naming HNSW, IVF, or DiskANN, though constraints 2 and 3 are exactly what would eliminate
HNSW. No quantified accuracy tradeoff — neither the over-fetch factor nor the error bounds are
given. No transactional detail on how splits and merges interact with MVCC, concurrent writers, or
isolation, despite that being the hard part inside a transactional database. Fanout "typically
around 100" is unexplained, and the deletion path gets nothing beyond merges. The embedded demo
video was not watched — out of scope for this read.

---

## Grading

- **Criterion 1 — PASS.** The Status section states plainly that merge operations and partition
  reassignments are not yet implemented, in the 25.2 preview.
- **Criterion 2 — FAIL.** The maintenance section presents "accuracy holds even after many cycles
  — start with an empty table, insert millions of vectors, and still get high accuracy" as the net
  claim, and nothing anywhere connects it to the fact recorded three sections later that merges
  and reassignments have not shipped. The omits section's "high accuracy is asserted" is a
  different observation: it flags an unmeasured claim, not a claim resting on unshipped machinery.
  A reader finishing the maintenance section carries away a durability property the 25.2 preview
  cannot currently deliver.
- **Criterion 3 — PASS.** Euclidean-only is stated in the Status section, with cosine and inner
  product planned.
- **Criterion 4 — PASS.** The `crdb_region` DDL is reproduced with `LOCALITY REGIONAL BY ROW`, and
  the toggle is noted.
- **Criterion 5 — PASS.** One bit per dimension, quantized relative to the partition centroid, with
  the no-global-retrain consequence.
