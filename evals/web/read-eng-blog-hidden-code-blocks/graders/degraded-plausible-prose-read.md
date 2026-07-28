# Degraded twin — plausible prose read (no rendered retrieval)

Fails criteria 1 and 2. Passes 3, 4, 5.

This is what a static fetch produces: every word of the prose, none of the artifacts. It reads
as a complete, careful notes file. Nothing in it is false.

---

# Value Separation in Pebble: Storage Engine Optimization

**Source:** https://www.cockroachlabs.com/blog/value-separation-pebble-optimization/ · Jackson
Owens & Annie Pompa, Cockroach Labs

## Problem

Pebble is CockroachDB's LSM-based key-value storage engine. Compactions run continuously in the
background, merge-sorting SSTables to keep read amplification under control, and they consume
CPU, read bandwidth, and a great deal of write bandwidth. The inefficiency the post identifies:
compaction sorts on keys alone and never inspects values, yet values are stored inline beside
their keys, so every compaction rewrites data the sort had no interest in. Workloads with large
values — wide rows, JSONB documents — pay this cost over and over as data moves down the LSM.

## Impact

Shipped in CockroachDB **v25.4**, delivering up to roughly **50%** storage-engine throughput
improvement on the `kv0/values=4096` benchmark — upserts against a `BIGINT` primary key with
**4 KiB** values. The nightly throughput series is flat around 5,800–6,300 ops/sec for six
months and steps to roughly 9,200–9,400 ops/sec at the point value separation is enabled,
consistent with the stated figure on identical hardware.

## Architecture

Values above a size threshold are written to a new file type, the **blob file**, instead of
inline in the SSTable. A blob file holds a series of value blocks plus an index block, both in
Pebble's columnar block format, which is similar to PAX. Where the value used to sit, the
SSTable now stores a small **value handle** identifying the blob file and the location of the
value within it.

The consequence is the entire point of the design: when a compaction encounters a separated
value, it copies the handle rather than the value. For a large value the handle is orders of
magnitude smaller, so the write bandwidth compaction spends on that record collapses. The cost
is on the read side — resolving a handle means an extra indirection from file to block to
value — so Pebble's iterators cache blob files and their blocks for the iterator's lifetime to
avoid paying the lookup twice.

SSTables that reference blob values carry an optional liveness index block, a run-length-encoded
bitmap per referenced blob file recording which values in that file are still live.

## Key decisions & tradeoffs

**1. Separate values, but reject the published designs.** WiscKey (FAST 2016) and LavaStore
(VLDB 2024) both demonstrated the write-amplification win. The post states neither was
appropriate for CockroachDB's workloads, and locates the difficulty precisely: separation itself
is not the hard part — the heuristics governing *when* to compact values are.

**2. Bound scan cost with blob reference depth.** A blob file starts out one-to-one with the
SSTable it was written beside, but later compactions fragment that mapping and scatter a
range's values across many blob files, which destroys cache effectiveness. Pebble tracks a
per-SSTable blob reference depth — the maximum number of blob files a scan must hold in its
working set at once. When depth grows too large, a compaction writes fresh blob files rather
than copying handles, resetting its outputs to depth 1. The rejected alternative is letting
locality rot indefinitely; the price paid is write bandwidth, spent deliberately to bound read
overhead.

**3. Reclaim space with blob file rewrite compactions.** Values whose keys were overwritten or
deleted are dead but still occupy their blob file, and the depth heuristic drops references
wholesale. A new compaction type ORs together the liveness bitmaps of every SSTable referencing
a blob file and rewrites it without the unreferenced values. The benefit is less pronounced when
values are homogeneous, since such files compress well already.

**4. Do not rewrite the referencing SSTables.** This is the sharpest decision in the post. When a
blob file is rewritten, the obvious move is to update every SSTable that points into it. That
alternative is rejected on two grounds: it is expensive, and it hands back precisely the write
bandwidth savings that justify the feature in the first place. Instead the handle survives
through indirection — the blob file ID is a stable logical identifier the LSM maps to a physical
file, the block ID is remapped through a special column in the rewritten index block, and the
value ID continues to index the original block. The consequence is that dead values cannot
actually be removed; they become empty values costing about two bytes each, with a value-ID
offset in the remapping allowing a leading run of them to be skipped entirely.

**5. Heuristics above the storage layer.** From v25.4 CockroachDB separates values of at least
256 bytes by default. Below that threshold it still separates parts of the keyspace that are
rarely read and latency-tolerant — the Raft log is the named example, since it is normally
served from memory until replicated. MVCC garbage is separated eagerly to improve locality for
reads at recent timestamps.

**6. An admitted unrealized benefit.** The MVCC-garbage separation does not fully pay off. The
SQL optimizer issues many `AS OF SYSTEM TIME` queries to collect statistics, and those queries
deliberately scan MVCC history; retrieving their separated values can dominate read bandwidth
and offset much of the theoretical benefit. The post names this as future work rather than
claiming the win. Storage tiering by data age is floated as a speculative future use of blob
files.

## Standards / refs / tech

WiscKey (Lu et al., FAST 2016); LavaStore (Wang et al., VLDB 2024); PAX (VLDB 2001). The post
permalinks several `cockroachdb/pebble` source locations for the handle, blob metadata, block,
and columnar-block implementations.

## Code / schemas

The post walks through the value handle's contents and the on-disk layout of blob files and
SSTables in the surrounding prose; the structural description above captures what it conveys.

## What the post omits

Only the win is quantified. Space amplification, write amplification, and read latency are
discussed qualitatively; the single throughput chart is the only measurement. The heuristics are
called "much of the complexity" and then never specified — no thresholds, no triggers, and the
blob reference depth bound is never given a value. One benchmark shape only, with nothing for
scan-heavy or read-dominant workloads. No discussion of which workloads regress given the
acknowledged read indirection, no cluster-setting names for disabling it, no compaction
scheduling detail, and no crash-recovery story for keeping blob files consistent with the
manifest.

---

## Grading

- **Criterion 1 — FAIL.** The `Handle` struct never appears. "The post walks through the value
  handle's contents ... in the surrounding prose" is exactly the paraphrase Step 3 forbids;
  `BlobFileID`, `ValueLen`, `BlockID`, `ValueID` are absent as a field list, and the Code /
  schemas section reproduces nothing. Note the failure is disguised: the prose does mention "blob
  file ID", "block ID" and "value ID" inside decision 4, which is why the criterion requires them
  as a reproduced code block and not as string presence.
- **Criterion 2 — FAIL.** No figure was opened. The 30-byte footer and its component sizes, the
  `Virtual blocks` / `Offsets` columns, and the liveness block's position in the SSTable layout
  are all absent. The liveness bitmap *is* described — from the prose, which states it — but no
  byte-level structure appears anywhere.
- **Criterion 3 — PASS.** `kv0/values=4096`, 4 KiB values, and v25.4 are all present, and the
  chart's ops/sec range is read off correctly. (The throughput figure is a hero image present in
  the static HTML; recovering it does not require rendering, which is why criterion 2 grades the
  two format diagrams specifically.)
- **Criterion 4 — PASS.** Decision 4 names the rejected alternative (rewriting the referencing
  SSTables) and both reasons. Decisions 2 and 3 also carry their alternatives.
- **Criterion 5 — PASS.** The AOST admission is carried in full, including the offsetting effect
  and its future-work status.
