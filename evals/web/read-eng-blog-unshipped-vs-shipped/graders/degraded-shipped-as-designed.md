# Degraded twin — design intent presented as shipped behaviour

Fails criteria 1 and 2. Passes 3, 4, 5.

The fluent summary. Every mechanism is described accurately, the JS-gated DDL is recovered,
Euclidean-only is noted, RaBitQ is explained with its actual mechanism. The defect is that the
architecture reads as a description of working software, because the status section was never
reconciled against it.

---

# C-SPANN: Real-Time Indexing for Billions of Vectors with CockroachDB

**Source:** https://www.cockroachlabs.com/blog/cspann-real-time-indexing-billions-vectors/ ·
published 23 June 2025

## Problem

Semantic search over user-generated content at billions-scale: millions of users, each holding
hundreds to thousands of items, expecting results instantly and expecting them fresh — upload
something, find it immediately. Existing vector solutions assume the dataset fits in memory on one
machine, or at worst on a fast local SSD. They do not expect data distributed across regions,
constantly changing, or embedded in a transactional system, and their limitations follow:
batched writes, stale results, specialized hardware.

An index is needed because embedding vectors have hundreds or thousands of dimensions and no
natural ordering — should beach photos sort before or after food photos? — so ordinary indexes do
not apply, and brute force stops being practical past tens of thousands of vectors.

## The six constraints

Each rules out a class of algorithm: no central coordinator, so any node can serve reads and
writes; no large in-memory structures, with state in persistent storage, which the post calls
especially important for Serverless; minimal network hops; a layout compatible with sharding onto
KV ranges; no hot spots; and incremental updates — real-time inserts and deletes without blocking,
rebuilds, or quality loss. Together these "ruled out many common approaches."

## Architecture

C-SPANN is "CockroachDB SPANN," drawing on Microsoft's SPANN and SPFresh papers and Google's
ScaNN.

**Hierarchical k-means tree.** Vectors are grouped into partitions of dozens to hundreds by
similarity, each with a centroid — the average of its members, their centre of mass. Centroids
cluster recursively into higher-level partitions. From the tree figure: each partition node holds
a fixed-width slot array of child partition IDs beside its centroid, uniform at every level, and
only leaf partitions hold actual vectors. The slot arrays are drawn partially filled, and that
headroom is what split and merge operate against.

**Storage mapping.** Each partition is a self-contained unit in the KV layer, laid out as a
contiguous set of key-value rows within a range, so ranges split, merge, and rebalance exactly
like any other table data. The partitions/nodes figure shows containment as node ⊃ range ⊃
partitions, explicitly not one partition per range: Node 2 holds two ranges, and Range 2
co-locates Partition 1 (the root) with Partition 2 — so tree level does not determine range
placement and co-resident partitions need not be tree-adjacent.

**Query path.** Start at the root, compare the query vector against that level's centroids,
descend into the closest matches, repeat to the leaves, scan the candidates. Partitions at each
level are processed in parallel, and because a partition's vectors are packed and similar by
design, SIMD instructions scan blocks efficiently. With a fanout around 100 the tree stays wide
and shallow — 1M vectors in 3 levels, 10B vectors in 5 — which is what delivers the
minimal-hops constraint. Partition rows are cached by the storage layer's block cache like any
other table data, with no specialized vector caching and no startup rebuild.

## Index maintenance

**Splits** run automatically in the background, dividing a partition's vectors into two roughly
equal groups with a balanced variant of k-means. The split figure adds what the text leaves out:
the parent's own centroid is recomputed — (0.5, 5.5) becomes (1.3, 4.7) — and that update
propagates upward to the root, so a leaf split is not merely a slot-list edit.

Partition splits are not range splits: the former is a logical unit grouping similar vectors to
improve search efficiency, the latter a physical unit of storage balancing capacity and access.
Adding nodes redistributes ranges at near-linear rates.

**Relocation after a split** comes from SPFresh. A vector near the boundary may end up closer to a
neighbouring partition's centroid than to either new one, and vice versa; the relocation figure
shows the exchange is bidirectional, with one vector moving each way. This is SPFresh's nearest
partition assignment.

**Merges** reassign vectors out of undersized partitions and remove them. Between splits,
relocation, and merges the index keeps its shape as data churns, and accuracy holds even after
many cycles — you can start with an empty table, insert millions of vectors, and still get high
accuracy.

## Quantization

An OpenAI embedding is 1,536 dimensions of 2-byte floats, about 3 KB per vector, and the greater
expense is the CPU and memory to scan full vectors rather than the storage itself. RaBitQ reduces
each dimension to a single bit — roughly 94%, about 3 KB down to about 200 bytes. Each vector is
quantized relative to its partition's centroid, which is why splits and merges only re-quantize
the affected partition rather than forcing a global retrain.

Four steps: a random orthogonal transform, which spreads skew while preserving angles and
distances; mean-centering on the partition centroid; normalization to unit length; and each
dimension reduced to a bit, zero if the value is negative and one otherwise. The RaBitQ figure
shows why the first step matters — the original 100-dimension vector trends upward and is nearly
all positive, so a sign bit would carry almost no information; after the transform the values are
symmetric noise about zero, roughly -8 to +7, giving the balanced bit string sign encoding needs.

Stored per vector: the bit string, the dot product between the quantized and original vectors, and
the exact distance from the centroid. Query vectors use a different asymmetric encoding at 4 bits
per dimension, SIMD-optimized. A reranking step then fetches the original full vectors to
recompute exact distances, over-fetching to compensate, with RaBitQ's error bounds determining how
many extras are needed.

## Per-owner indexes and multi-region

Most queries are scoped to a single owner, and including other users' vectors "could be a security
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

The `<->` operator is pgvector-compatible. Performance is proportional to the vectors owned by
that user, not the total, because the index maintains a separate k-means tree per distinct user —
"there isn't much difference between 1 billion vectors in a single tree or the same number spread
across a million smaller trees."

Composing with multi-region:

```sql
CREATE TABLE photos (
  id UUID PRIMARY KEY,
  user_id UUID,
  embedding VECTOR(1536),
  VECTOR INDEX (crdb_region, user_id, embedding)
) LOCALITY REGIONAL BY ROW;
```

`crdb_region` is added automatically and joins the index columns, co-locating table and index rows
per region — a latency win and a data-domiciling mechanism.

## Status

Vector indexing is in preview in 25.2. Root partition caching, expanded SIMD, and contention
minimization are called out as areas for further work. Planned additions include `IMPORT`, `ALTER
INDEX`, wider `WHERE` filter patterns, and cosine plus inner-product metrics — **Euclidean
distance is the only metric supported today**, which matters for anyone embedding with models
where cosine is conventional.

## What the post omits

No performance numbers at all — no QPS, latency percentiles, recall measurements, or build times.
"Near-linear," "high accuracy," and "94%" are asserted rather than measured here; the 94% is an
algorithmic property for common cases, not a result on their workload. No named comparison: the
constraints "ruled out many common approaches" but HNSW, IVF, and DiskANN are never mentioned,
even though constraints 2 and 3 are precisely what would eliminate HNSW. No quantified accuracy
tradeoff — neither the over-fetch factor nor RaBitQ's error bounds are given. No transactional
detail on how splits and merges interact with MVCC, concurrent writers, or isolation, despite that
being the hard part of doing this inside a transactional database. The fanout of "typically around
100" is unexplained and untuned, and the deletion path gets no detail beyond merges. The embedded
demo video was not watched — out of scope for this read.

---

## Grading

- **Criterion 1 — FAIL.** Merges and partition reassignments are described in the maintenance
  section as working parts of the index ("Merges reassign vectors out of undersized partitions and
  remove them"), and the Status section lists only root partition caching, SIMD, and contention as
  further work. That merges and partition reassignments are *unimplemented in 25.2* never appears.
  Note the disguise: the Status section is present and accurate about everything else, so the
  output looks like it handled shipped-vs-planned carefully.
- **Criterion 2 — FAIL.** The accuracy claim ("accuracy holds even after many cycles — start with
  an empty table, insert millions of vectors, and still get high accuracy") is repeated as an
  established property, with no note that it partly rests on maintenance operations that have not
  shipped. The omits section does say "high accuracy is asserted rather than measured," which is
  a different point — an unmeasured claim about shipped behaviour, not a claim resting on unshipped
  behaviour.
- **Criterion 3 — PASS.** Euclidean-only in 25.2 is stated explicitly, with cosine and inner
  product as planned.
- **Criterion 4 — PASS.** The `crdb_region` DDL is reproduced in full with `LOCALITY REGIONAL BY
  ROW`.
- **Criterion 5 — PASS.** One bit per dimension and quantization relative to the partition
  centroid are both stated, along with why that avoids global retraining.
