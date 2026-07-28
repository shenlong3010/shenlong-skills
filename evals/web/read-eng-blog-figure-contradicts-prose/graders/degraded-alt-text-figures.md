# Degraded twin — plot described, not read

Fails criterion 2. Passes 1, 3, 4, 5.

Catches the price discrepancy, comprehends the window functions, names the missing DDL,
reproduces the schema. The isolated defect: the PCA plot is described by what it depicts rather
than read for the numbers printed on its axes, and the conclusion drawn from it — "some variance
is lost" — is one anybody could reach without opening the image.

---

# Visual Vehicle Search with SQL and Vector Embeddings

**Source:** https://www.cockroachlabs.com/blog/vehicle-search-sql-vector-embeddings/ · Alejandro
Infanzon, Solutions Architect, Cockroach Labs

## Problem

Keyword search fails the buyer who will know it when they see it. "A car that looks like this
photo" is not a text query, and any text match is hostage to whether the seller typed "vintage
muscle" into the listing. The thesis is architectural: metadata filtering and vector similarity
should resolve in one ACID SQL statement, with no separate vector database and no embedding
service in the query path.

## Architecture

Images move from a Kaggle/GitHub dataset into a staging table; CLIP embeddings and synthetic
Faker metadata are generated and inserted into `for_sale_inventory`. At query time the user copies
an image to the clipboard, the app embeds it with CLIP, and a KNN query runs in CockroachDB using
the `<->` operator with the price filter in the same statement.

The C-SPANN index figure shows a three-level hierarchical k-means tree: root Partition 1, centroid
(5.8, 5.5), branching to Partitions 10 (9.5, 6.8) and 11 (2.1, 4.1), and from there to five leaf
partitions holding actual vectors — P8, centroid (0.8, 0.8), holds Vectors 21, 24, 29 and 31.
Slots are drawn with headroom and the branching factor is non-uniform. A centroid is the mean of
its partition's members, so search descends by comparing against centroids rather than scanning
everything. One illustration typo: "Vector 22" appears under both Partition 3 and Partition 5 with
different coordinates.

## Key decisions & tradeoffs

- **Vectors in the OLTP store rather than a dedicated vector database.** One ACID statement covers
  the price filter and the similarity ordering, so there is no dual-write consistency problem.
  Asserted, never benchmarked.
- **CLIP `clip-ViT-B-32`.** Shared image/text space, so one column supports text-to-image and
  image-to-image — only the latter is demoed.
- **L2 over cosine.** Unjustified, and notable given cosine is conventional for CLIP.
- **Filter and sort in one statement.** The stated payoff; the filtered-ANN recall hazard is never
  mentioned.
- **PCA to three dimensions, visualization only.** The serving path keeps full `VECTOR(512)`.

## Code / schemas (verbatim)

The DDL and the KNN query are absent from the rendered DOM — they sit JSON-escaped in an embedded
Contentful payload.

```sql
CREATE TABLE public.for_sale_inventory (
    vin STRING NOT NULL, make STRING NULL, model STRING NULL, color STRING NULL
  , registration_date STRING NULL, year INT4 NULL, price_in_usd INT4 NULL
  , power_kw INT4 NULL, power_ps INT4 NULL, transmission_type STRING NULL
  , fuel_type STRING NULL, fuel_consumption_l_100km STRING NULL
  , fuel_consumption_g_km INT4 NULL, mileage_in_km DECIMAL NULL
  , offer_description STRING NULL, image_data BYTES NULL
  , image_embedding VECTOR(512) NULL, image_file_name STRING NULL
  , CONSTRAINT for_sale_inventory_pkey PRIMARY KEY (vin));
```

```sql
WITH RankedInventory AS (
    SELECT inv.vin, inv.make, inv.model, inv."year", inv.price_in_usd
         , inv.image_data, inv.offer_description
         , inv.image_embedding <-> '[0.486967,0.577628,-0.197629, ...]' AS distance
    FROM for_sale_inventory inv
    WHERE inv.price_in_usd BETWEEN 10000 AND 500000
    ORDER BY distance ASC LIMIT 20
) SELECT vin, make AS "Make", model AS "Model", "year" AS "Year"
       , price_in_usd AS "Price", image_data, offer_description AS "Description"
       , distance AS "Similarity Score"
       , CASE WHEN (MAX(distance) OVER () - MIN(distance) OVER ()) = 0 THEN 5.0
           ELSE CEIL(1.0 + 4.0 * (MAX(distance) OVER () - distance) / (MAX(distance) OVER () - MIN(distance) OVER ()))
         END AS "Closeness Rating"
  FROM RankedInventory ORDER BY distance ASC;
```

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('clip-ViT-B-32')
```

The "Closeness Rating" is batch-relative, not absolute: the `CASE` min-max rescales distance into
a 1–5 band using `MAX(distance) OVER ()` and `MIN(distance) OVER ()`, windows computed over the
returned rows. Change `LIMIT` and the same car's rating changes; a 5 means "closest in this result
set," nothing more. The probe vector is string-interpolated into the SQL rather than parameterized.
`registration_date` is a `STRING`, and `image_data BYTES` sits inline beside the embedding.

## Results (from the figures)

Query image: a black supercharged Dodge Charger. Sliders: 20 results, $27,000–$216,000. Six
late-1960s muscle cars across four makes match on visual form alone, with L2 distances the prose
omits — 1969 Pontiac Firebird 3.8773, 1969 Camaro 4.1694, 1966 Chevrolet Sport 4.3706, 1968 GTO
4.6288, 1964 Oldsmobile Jetstar 88 4.7320, 1967 Firebird 4.7451.

**The post contradicts itself on price.** The body text lists the 1969 Camaro at $335,000; the
result screenshot shows **$33,445**. The screenshot is the one to trust — $335,000 would also fall
outside the app's own $27k–$216k slider band visible in the same image, so the prose figure cannot
be what the demo returned.

A 3D scatter plot follows, showing the PCA projection of the embedding space with the query vector
and its neighbours plotted as points; visually similar cars cluster together, which is the
intuition the post wants to convey. Projecting 512 dimensions down to three inevitably discards
information, so the plot should be read as illustrative rather than as a faithful picture of the
space the index actually searches.

## What the post omits

No performance numbers at all — no latency, QPS, recall, or brute-force comparison. Specifically,
**no `CREATE VECTOR INDEX` DDL appears**: the schema declares `image_embedding VECTOR(512)` and
stops, so it is not stated whether the demo table has a vector index or is doing an exact scan
over its 4,597 rows — a rounding error against the "billions of vectors" its own linked companion
post addresses. Also absent: embedding cost and ingest throughput, any L2-vs-cosine
justification, the filtered-ANN recall caveat, a repo link, and every line of application code
(clipboard capture, probe embedding, psycopg connection, Faker generator, visualization — all
narrated, none shown). Metadata is synthetic, so only the image similarity is real. Multi-region
resilience is claimed by inheritance and never demonstrated; text-to-image search is never demoed
despite being the stated reason for choosing CLIP.

---

## Grading

- **Criterion 1 — PASS.** Both values appear ($335,000 in the prose, $33,445 in the screenshot),
  the disagreement is stated explicitly, and the screenshot is identified as authoritative with
  the slider-band check as supporting evidence.
- **Criterion 2 — FAIL.** The PCA plot is described by subject matter — points, clustering,
  illustrative intent — and never by its axis labels. PC2 (7.38%) and PC3 (6.35%) do not appear.
  The conclusion offered ("projecting 512 dimensions down to three inevitably discards
  information") is generic and reachable without opening the figure, which is precisely what the
  criterion excludes. The prose's competing claim that the projection "retains the most
  significant variance" is never confronted with a number.
- **Criterion 3 — PASS.** The rating is identified as batch-relative with the `LIMIT`-sensitivity
  spelled out.
- **Criterion 4 — PASS.** The missing `CREATE VECTOR INDEX` is named, with the exact-scan
  ambiguity and the row count.
- **Criterion 5 — PASS.** `VECTOR(512)` and `<->` reproduced literally.
