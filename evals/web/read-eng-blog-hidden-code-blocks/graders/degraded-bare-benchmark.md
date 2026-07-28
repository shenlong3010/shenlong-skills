# Degraded twin — bare benchmark number

Fails criterion 3. Passes 1, 2, 4, 5.

Full-fidelity retrieval: the hidden Go struct is recovered, the format diagrams are read for
byte-level structure, the tradeoffs carry their rejected alternatives, the honest admission
survives. The single defect is the headline number reported without the conditions that give it
meaning — the most common way a technically thorough read still misleads.

---

# Value Separation in Pebble: Storage Engine Optimization

**Source:** https://www.cockroachlabs.com/blog/value-separation-pebble-optimization/ · Jackson
Owens & Annie Pompa, Cockroach Labs

## Problem

Pebble is CockroachDB's LSM storage engine. Background compactions merge-sort SSTables to hold
down read amplification, spending CPU, read bandwidth, and write bandwidth to do it. The waste:
compaction sorting is a function of keys only and never inspects values, but values live inline
beside their keys, so every compaction rewrites bytes the sort never looked at. Large-value
workloads — wide rows, JSONB — pay it repeatedly.

## Impact

Value separation delivers **up to a 50% storage-engine throughput improvement**. The
accompanying chart shows a flat nightly series stepping sharply upward at the point the feature
is enabled, and holding there.

## Architecture

**Blob files** are a new file type holding separated values: a series of value blocks, an index
block, and a 30-byte footer. Both index and value blocks use Pebble's columnar block format,
similar to PAX, which gives constant-time lookup by block ID and value ID.

The footer's layout, read from the BLOB FILE FORMAT diagram, is: CRC (4 bytes), index block
offset (8 bytes), index block length (8 bytes), checksum type (1 byte), format (1 byte), magic
string (8 bytes). The index block itself holds two parallel columnar structures — a `Virtual
blocks` column of `M` entries mapping index → (block index, valueIDoffset), and an `Offsets`
column of `N+1` entries mapping index → offset. That `valueIDoffset` column is the machinery
behind decision 4 below.

**Value handles** replace the value in the SSTable KV:

```go
// Handle describes the location of a value stored within a blob file.
type Handle struct {
  BlobFileID base.BlobFileID
  ValueLen   uint32
  // BlockID identifies the block within the blob file containing the value.
  BlockID BlockID
  // ValueID identifies the value within the block identified by BlockID.
  ValueID BlockValueID
}
```

On compaction Pebble usually copies the handle rather than the value; for a large value the
handle is orders of magnitude smaller, and that is the entire win. On read the handle costs an
extra indirection — file, then block, then value — so iterators cache blob files and blocks for
the iterator's lifetime rather than repeating the lookup.

**SSTable side.** The SSTABLE FILE FORMAT diagram shows an optional Blob Reference Value
Liveness Index Block sitting between the data blocks and the meta/properties blocks: a
run-length-encoded bitmap per referenced blob file marking which values remain live. The SSTable
footer carries `Attributes (4 bytes, Pebblev7+)` and a `Checksum: CRC over footer data (4 bytes,
Pebblev6+)`.

## Key decisions & tradeoffs

**1. Separate values, but reject the published designs.** WiscKey (FAST 2016) and LavaStore
(VLDB 2024) both proved the write-amplification win; the post states neither suited CockroachDB's
workloads. The hard part is explicitly not separation but the heuristics of when to compact
values.

**2. Bound scan cost via blob reference depth.** Blob files begin one-to-one with an output
SSTable, but later compactions fragment the mapping and scatter values, killing cache
effectiveness. Pebble tracks per-SSTable blob reference depth — the maximum number of blob files
in a scan's working set. When it grows large, a compaction writes new blob files instead of
copying handles, resetting outputs to depth 1. The alternative — letting locality degrade — is
rejected; the price is write bandwidth spent to bound read overhead.

**3. Blob file rewrite compactions** reclaim space amplification from dead values: those whose
keys were overwritten or tombstoned, plus references the depth heuristic dropped wholesale.
Pebble ORs the liveness bitmaps of every SSTable referencing the file and drops what nothing
points at. The effect is smaller when values are homogeneous, since such files already compress
well.

**4. Do not rewrite the referencing SSTables — the sharpest decision.** The obvious approach,
updating every SSTable that points into a rewritten blob file, is rejected as expensive *and* as
returning the very write-bandwidth savings that justify the feature. Handles survive through
three indirections instead: `BlobFileID` is a stable logical ID the LSM maps to a physical file;
`BlockID` is remapped by a special column in the rewritten index block; and `ValueID` still
indexes the *original* block, which means dead values cannot be removed at all — they become
empty values costing roughly 2 bytes each, with the `valueIDoffset` letting a leading run of them
be skipped.

**5. CockroachDB-level heuristics beyond size.** Values of at least **256 bytes** are separated
by default. Below that, rarely-read latency-tolerant keyspace is still separated — the Raft log
is the named example, normally in memory until replicated. MVCC garbage is separated eagerly for
locality on recent-timestamp reads.

**6. Admitted unrealized benefit.** The MVCC-garbage separation does not fully pay off: the SQL
optimizer issues many `AS OF SYSTEM TIME` queries for statistics, those queries deliberately scan
MVCC history, and retrieving their separated values "can dominate read bandwidth, offsetting much
of the theoretical benefit." Named as future work, not claimed as a win. Storage tiering by data
age is floated speculatively.

## Standards / refs / tech

WiscKey (Lu et al., FAST 2016) · LavaStore (Wang et al., VLDB 2024) · PAX (VLDB 2001) · five
permalinked `cockroachdb/pebble` locations covering `handle.go`, `blob_metadata.go`, `blocks.go`,
`raw_bytes.go`, and `sstable/colblk`.

## What the post omits

Only the throughput win is quantified — space amplification, write amplification, and read
latency stay qualitative. The heuristics are called most of the complexity and then never
specified: no thresholds, no triggers, and no stated bound for blob reference depth; the 256-byte
default is the only concrete number. No regression discussion for workloads that get worse under
the read indirection, no cluster-setting names, no compaction scheduling, and no crash-recovery
story for keeping blob files consistent with the manifest. The AOST conflict is described but not
sized and has no timeline.

---

## Grading

- **Criterion 1 — PASS.** The `Handle` struct appears as a code block with all four fields and
  its comments.
- **Criterion 2 — PASS.** The 30-byte footer is broken into its six components, the index block's
  `Virtual blocks` / `Offsets` columns are named, and the liveness block's position plus the
  SSTable footer's version-gated fields are recovered. All of this is figure-only content.
- **Criterion 3 — FAIL.** "Up to a 50% storage-engine throughput improvement" appears with no
  workload (`kv0/values=4096`), no value size (4 KiB), and no version (v25.4). The chart is
  described only in shape. The criterion requires at minimum the value size and the version; both
  are absent. This is the isolated defect.
- **Criterion 4 — PASS.** Decision 4 states the rejected alternative and both reasons; decisions
  2 and 3 also carry theirs.
- **Criterion 5 — PASS.** The AOST admission is carried with the quoted offsetting effect and its
  future-work status.
