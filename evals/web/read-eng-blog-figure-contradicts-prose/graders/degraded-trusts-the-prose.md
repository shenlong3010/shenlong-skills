# Degraded twin — trusts the prose over the figure

Fails criterion 1. Passes 2, 3, 4, 5.

Everything a rigorous read should do is done here: the PCA axes are read off the plot, the window
functions are understood, the missing DDL is named, the schema is reproduced literally. The one
defect is that the results screenshot was looked at but the price was taken from the body text —
the failure mode that survives an otherwise careful read.

---

# Visual Vehicle Search with SQL and Vector Embeddings

**Source:** https://www.cockroachlabs.com/blog/vehicle-search-sql-vector-embeddings/ · Alejandro
Infanzon, Solutions Architect, Cockroach Labs

## Problem

Keyword search cannot serve the buyer who knows what they want only when they see it. "A car that
looks like this photo" is not expressible as text, and a text match depends on whether the seller
happened to type "vintage muscle" into the listing description. The architectural thesis: metadata
filtering and vector similarity belong in one ACID SQL statement, with no separate vector database
and no external embedding service in the query path.

## Architecture

Ingest pulls images from a Kaggle/GitHub dataset into a staging table, generates CLIP embeddings
and synthetic metadata via Faker, and inserts into `for_sale_inventory`. At query time the user
copies an image to the clipboard, the app embeds it with CLIP, and a KNN query runs in
CockroachDB using the `<->` operator with the price filter applied in the same statement.

The C-SPANN index figure shows a three-level hierarchical k-means tree: root Partition 1 with
centroid (5.8, 5.5) branching to Partitions 10 (9.5, 6.8) and 11 (2.1, 4.1), which lead to five
leaf partitions holding the actual vectors — P8, centroid (0.8, 0.8), holds Vectors 21, 24, 29 and
31. Slots are drawn with visible headroom and the branching factor is non-uniform. A partition's
centroid is the mean of its members, so search descends by comparing against centroids instead of
scanning every vector. The figure has an internal inconsistency worth flagging: "Vector 22" is
drawn under both Partition 3 and Partition 5 with different coordinates, which is an illustration
typo.

## Key decisions & tradeoffs

- **Vectors in the OLTP store rather than a dedicated vector database.** Chosen because one ACID
  statement covers both `WHERE price_in_usd BETWEEN ...` and the `<->` ordering, eliminating the
  dual-write consistency problem. Asserted throughout, never benchmarked against the alternative.
- **CLIP `clip-ViT-B-32`.** A shared image/text embedding space, so a single column supports
  text-to-image and image-to-image search — though only image-to-image is demonstrated.
- **L2 distance over cosine.** No justification is offered, which is notable given cosine is the
  conventional choice for CLIP embeddings.
- **Filtering and ordering in one statement.** Presented as the payoff. The filtered-ANN recall
  hazard — a restrictive `WHERE` interacting badly with approximate search — is never raised.
- **PCA to three dimensions for visualization only.** The serving path keeps the full
  `VECTOR(512)` column.

## Code / schemas (verbatim)

Two of the four code blocks — the DDL and the KNN query — are absent from the rendered DOM
entirely; they live JSON-escaped inside an embedded Contentful payload.

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

The "Closeness Rating" is not an absolute score. The `CASE` is a min-max rescale into a 1–5 band
computed with `MAX(distance) OVER ()` and `MIN(distance) OVER ()` — windows over the returned
batch — so the same car's rating changes when `LIMIT` changes, and a rating of 5 only means
"closest in this result set." The probe vector is string-interpolated into the SQL rather than
parameterized. `registration_date` is typed `STRING`, and `image_data BYTES` sits inline in the
same row as the embedding.

## Results (from the figures)

The query image is a black supercharged Dodge Charger; the sliders are set to 20 results and a
$27,000–$216,000 price band. Six late-1960s muscle cars come back across four different makes,
matched on visual form alone: a 1969 Pontiac Firebird at distance 3.8773, a **1969 Chevrolet
Camaro at 4.1694, priced at $335,000**, a 1966 Chevrolet Sport at 4.3706, a 1968 GTO at 4.6288, a
1964 Oldsmobile Jetstar 88 at 4.7320 and a 1967 Firebird at 4.7451.

The 3D PCA plot is more revealing than the prose around it. Its axes are labelled **PC2 (7.38%)**
and **PC3 (6.35%)** — single-digit shares of variance, which quantitatively undercuts the body
text's claim that the projection "retains the most significant variance." 512-dimensional CLIP
space does not compress into three dimensions cleanly, and the axis labels say so directly.

## What the post omits

No performance numbers of any kind: no latency, QPS, recall, or comparison against brute force.
More specifically, **no `CREATE VECTOR INDEX` DDL appears anywhere** — the schema declares
`image_embedding VECTOR(512)` and nothing else, so it is not even stated whether the demo table
carries a vector index or is doing an exact scan over its 4,597 rows. That scale is a rounding
error against the "billions of vectors" its own linked companion post addresses, which makes the
omission load-bearing rather than incidental. Also missing: embedding cost and ingest throughput,
any justification for L2 over cosine, the filtered-ANN recall caveat, a repository link, and all
application code — clipboard capture, probe embedding, the psycopg connection, the Faker
generator and the visualization are narrated but never shown. Metadata is synthetic, so only the
image similarity is real. Multi-region resilience is claimed by inheritance in the conclusion and
never demonstrated, and text-to-image search is never demoed despite being the stated reason for
choosing CLIP.

---

## Grading

- **Criterion 1 — FAIL.** The Camaro is reported at $335,000, taken from the body text. The
  screenshot's $33,445 never appears and no discrepancy is flagged. The failure is disguised by
  the fact that the results screenshot clearly *was* read — all six L2 distances are transcribed
  off it, including the Camaro's own 4.1694, along with the slider settings — so this is not a run
  that skipped the figure. It read the figure, took the distance from it, and still deferred to
  the prose for the price in the same sentence. Note also that
  $335,000 falls outside the app's own $27k–$216k slider band shown in the same screenshot,
  which is the internal check that should have caught it.
- **Criterion 2 — PASS.** PC2 (7.38%) and PC3 (6.35%) are read off the axes and correctly framed
  as undercutting the prose claim.
- **Criterion 3 — PASS.** The rating is explicitly identified as batch-relative, with the
  `LIMIT`-sensitivity spelled out.
- **Criterion 4 — PASS.** The missing `CREATE VECTOR INDEX` is named specifically, with the
  exact-scan ambiguity and the 4,597-row scale.
- **Criterion 5 — PASS.** `VECTOR(512)` and `<->` are reproduced literally in the DDL and query.
