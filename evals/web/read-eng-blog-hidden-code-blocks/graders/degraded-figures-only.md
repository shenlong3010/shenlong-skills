# Degraded twin — figures retrieved, Contentful code blocks missed

Fails criterion 1. Passes 2, 3, 4, 5.

The natural partial success on this platform. Cockroach Labs serves figures as ordinary
full-resolution assets reachable straight from `src`, while code blocks are JSON-escaped inside an
embedded Contentful payload — two different retrieval problems. This output solves the first and
not the second, so the byte-level diagram structure is all present and the Go struct is paraphrased
into prose. Exists to prove criterion 1 fails independently of criterion 2.

---

# Value Separation in Pebble: Storage Engine Optimization

**Source:** https://www.cockroachlabs.com/blog/value-separation-pebble-optimization/ · Jackson
Owens & Annie Pompa, Cockroach Labs

## Problem

Pebble is CockroachDB's LSM-based storage engine. Compactions run continuously in the background,
merge-sorting SSTables to hold read amplification down, and they spend CPU, read bandwidth, and a
great deal of write bandwidth doing it. The waste the post identifies: compaction sorting is a
function of keys only and never inspects values, yet values sit inline beside their keys, so every
compaction rewrites bytes the sort never looked at. Large-value workloads — wide rows, JSONB —
pay this repeatedly as data moves down the LSM.

## Impact

Shipped in CockroachDB **v25.4**, up to roughly **50%** storage-engine throughput improvement,
workload-dependent. The benchmark chart plots ops/sec over 01/01–07/01 2025 for `kv0/values=4096`
— upserts against a `BIGINT` primary key with **4 KiB** values. It sits flat at ~5,800–6,300
ops/sec for six months, then steps near-vertically at the annotated "Value Separation enabled"
point to ~9,200–9,400 ops/sec and holds, consistent with ~47% on identical hardware.

## Architecture

**Blob files** are a new file type holding separated values: a series of value blocks, an index
block, and a footer. Both index and value blocks use Pebble's columnar block format, similar to
PAX, giving constant-time lookup by block ID and value ID.

The BLOB FILE FORMAT diagram gives the on-disk layout the prose skips. The footer is **30 bytes**:
CRC (4 bytes), index block offset (8 bytes), index block length (8 bytes), checksum type (1 byte),
format (1 byte), and a magic string (8 bytes). The index block holds two parallel columnar
structures — a `Virtual blocks` column of `M` entries mapping index → (block index,
`valueIDoffset`), and an `Offsets` column of `N+1` entries mapping index → offset. That
`valueIDoffset` column is the machinery behind decision 4 below, and it appears nowhere in the
body text.

**Value handles** replace the value in the SSTable KV. Rather than the value itself, the SSTable
stores a compact handle identifying which blob file holds the value, how long the value is, which
block within that file contains it, and which value within that block it is. On compaction Pebble
usually copies the handle rather than the value; for a large value the handle is orders of
magnitude smaller, and that is where the win comes from. On read the handle costs an extra
indirection — file, then block, then value — so iterators cache blob files and their blocks for
the iterator's lifetime rather than repeating the lookup.

**SSTable side.** The SSTABLE FILE FORMAT diagram shows an optional Blob Reference Value Liveness
Index Block sitting between the data blocks and the meta/properties blocks — a run-length-encoded
bitmap per referenced blob file marking which values remain live. The SSTable footer carries
`Attributes (4 bytes, Pebblev7+)` and a `Checksum: CRC over footer data (4 bytes, Pebblev6+)`,
both version-gated in a way the prose never mentions.

## Key decisions & tradeoffs

**1. Separate values, but reject the published designs.** WiscKey (FAST 2016) and LavaStore
(VLDB 2024) both proved the write-amplification win; the post states neither was appropriate for
CockroachDB's workloads. The hard part is explicitly not separation but the heuristics of when to
compact values.

**2. Bound scan cost via blob reference depth.** Blob files begin one-to-one with an output
SSTable, but later compactions fragment that mapping and scatter values, destroying cache
effectiveness. Pebble tracks a per-SSTable blob reference depth — the maximum number of blob files
in a scan's working set. When it grows large, a compaction writes new blob files instead of
copying handles, resetting outputs to depth 1. The rejected alternative is letting locality decay;
the price is write bandwidth spent deliberately to bound read overhead.

**3. Blob file rewrite compactions** reclaim space amplification from dead values — those whose
keys were overwritten or tombstoned, plus references the depth heuristic dropped wholesale. Pebble
ORs together the liveness bitmaps of every SSTable referencing the file and drops what nothing
points at. The effect is less pronounced under high value homogeneity, since such files already
compress well.

**4. Do not rewrite the referencing SSTables — the sharpest decision.** The obvious move, updating
every SSTable that points into a rewritten blob file, is rejected as expensive *and* as giving back
precisely the write-bandwidth savings that justify the feature. Handles survive through three
indirections instead: the blob file ID is a stable logical ID the LSM maps to a physical file; the
block ID is remapped by a special column in the rewritten index block; and the value ID still
indexes the *original* block, which means dead values cannot be removed at all — they become empty
values costing roughly 2 bytes each, with the `valueIDoffset` from the index block letting a
leading run of them be skipped entirely.

**5. CockroachDB-level heuristics beyond size.** From v25.4, values of at least **256 bytes** are
separated by default. Below that, rarely-read latency-tolerant keyspace is still separated — the
Raft log is the named example, normally in memory until replicated. MVCC garbage is separated
eagerly to improve locality for recent-timestamp reads.

**6. Admitted unrealized benefit.** The MVCC-garbage separation does not fully pay off: the SQL
optimizer issues many `AS OF SYSTEM TIME` queries for statistics, those queries deliberately scan
MVCC history, and retrieving their separated values "can dominate read bandwidth, offsetting much
of the theoretical benefit." Named as future work rather than claimed as a win. Storage tiering by
data age is floated speculatively.

## Standards / refs / tech

WiscKey (Lu et al., FAST 2016) · LavaStore (Wang et al., VLDB 2024) · PAX (VLDB 2001) · five
permalinked `cockroachdb/pebble` source locations covering the handle, blob metadata, block, and
columnar-block implementations.

## Code / schemas

The post introduces a Go type describing the handle's contents; the four pieces of information it
carries are covered in the Architecture section above. No code block was recoverable from the
page.

## What the post omits

Only the throughput win is quantified — space amplification, write amplification, and read latency
stay qualitative, and the single chart is the only measurement. The heuristics are called most of
the complexity and then never specified: no thresholds, no triggers, no stated bound for blob
reference depth, with the 256-byte default the only concrete number. One benchmark shape only,
nothing for scan-heavy or read-dominant workloads, and it is an uncontrolled nightly time series
rather than an A/B on identical builds. No regression discussion for workloads that get worse
under the read indirection, no cluster-setting names, no compaction scheduling, and no
crash-recovery story for keeping blob files consistent with the manifest. The AOST conflict is
described but never sized and has no timeline.

---

## Grading

- **Criterion 1 — FAIL.** The `Handle` struct never appears as a code block. The Architecture
  section paraphrases its four fields into prose — "which blob file holds the value, how long the
  value is, which block within that file contains it, and which value within that block it is" —
  which is semantically complete and still exactly the paraphrase Step 3 forbids. `BlobFileID`,
  `ValueLen`, `BlockID`, and `ValueID` do not appear as identifiers anywhere; the Code / schemas
  section reproduces nothing and says so. This is the isolated defect, and note it is a *harder*
  failure to spot than the first twin's: the information is all there, only the searchable handles
  are gone.
- **Criterion 2 — PASS.** Both format diagrams are read for structure absent from the prose: the
  30-byte footer decomposed into its six components, the index block's `Virtual blocks` /
  `Offsets` columns with the `valueIDoffset`, the liveness block's position in the SSTable layout,
  and the version-gated footer fields.
- **Criterion 3 — PASS.** `kv0/values=4096`, 4 KiB values, and v25.4 all present, with the chart's
  ops/sec range read off correctly.
- **Criterion 4 — PASS.** Decision 4 names the rejected alternative and both reasons; decisions 2
  and 3 also carry theirs.
- **Criterion 5 — PASS.** The AOST admission is carried with the quoted offsetting effect and its
  future-work status.
