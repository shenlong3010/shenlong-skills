---
name: read-image
description: Extract structured content from raster images — screenshots, charts, diagram photos, whiteboards, UI mockups, document photos. Use whenever an image's CONTENT must be understood and reported, not just seen — "what does this screenshot show", "read this chart", "extract the architecture from this whiteboard photo", "what's in this image". Classifies the image type and applies a per-type extraction procedure with explicit uncertainty. Routes verbatim bulk text to image-ocr and text-format diagram files to read-diagram.
derivation: original
---

# Read Image

Native vision sees the image; this skill is the *discipline* for turning what is seen into structured, honest output. The failure mode it prevents: confident prose that silently invents values the image doesn't legibly contain.

## Step 1 — classify, then say so

Name the type before extracting: **chart/graph**, **screenshot/UI**, **diagram photo/whiteboard**, **document photo/scan**, **table photo**, or **general photo**. The type selects the procedure below. Mixed images (a slide containing a chart): decompose into regions and run each region's procedure.

## Per-type procedures

**Chart / graph**
- Report: chart type, axes with units and ranges, each series' name, the trend in one sentence, and notable points (peaks, crossovers, discontinuities).
- Approximate values as a small table,, each value marked `≈` — reading pixels is estimation, and the output must look like estimation. Never report more significant figures than the axis gridlines support.
- If the legend or an axis label is cropped/illegible, say which — a chart with unknown units is a shape, not data.

**Screenshot / UI**
- Report: application context (what app/page, inferred how), the current state (what the user was doing), any error/dialog text **verbatim in quotes**, and the interactive elements relevant to the question.
- Error text matters exactly — transcribe character-for-character; a paraphrased error message can't be searched.
- Dense text regions (logs, config files in a terminal screenshot): route to **image-ocr** for verbatim extraction rather than retyping by eye.

**Diagram photo / whiteboard**
- Extract into the read-diagram schema: nodes (id, label), edges (source → target, label, direction), hierarchy/groupings, anomalies.
- Whiteboards are messy: mark illegible labels as `[illegible]` rather than guessing, and flag arrows whose direction is ambiguous.
- Offer the round trip: the extracted structure can be re-emitted as Mermaid via gen-diagram — a photographed whiteboard becomes a versionable diagram.

**Document photo / scan**
- Verbatim text is image-ocr's job — route there. This skill reports layout and identity: what document, which sections visible, signatures/stamps present, quality issues that will hurt OCR (skew, shadow, cutoff).

**Table photo**
- Reconstruct as a markdown table; mark unreadable cells `?`. State row/column counts so truncation is visible. Numeric columns: same `≈` discipline as charts if the photo is low-quality.

**General photo**
- Objects, text-in-scene (verbatim, quoted), spatial relations relevant to the question. No inventory dumps — extract what the question needs.

## Output contract

Every extraction ends with an **Uncertainties** line: what was illegible, cropped, ambiguous, or estimated. An empty uncertainties line on a phone photo of a whiteboard is a credibility failure, not a success.

## Boundaries

- Bulk verbatim text from an image → **image-ocr** (deterministic, JSON output).
- Diagram *files* (.mmd, .puml, .svg, Lucid exports) → **read-diagram** (they're text; don't screenshot them).
- Regenerating or editing a diagram from the extraction → **gen-diagram**.
