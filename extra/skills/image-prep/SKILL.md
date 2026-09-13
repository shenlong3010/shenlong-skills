---
name: image-prep
description: Preprocess images before vision or OCR — downscale huge screenshots, crop to the region that matters, split multi-panel captures, boost contrast for faint text. Use when an image is >2000px on a side, a screenshot contains many windows/panels but one matters, OCR returns garbage on readable-looking text, or a diagram photo is skewed/dim — prep first, then re-run the read.
derivation: original
flow: lookup
domain: media
---

# Image Prep

Vision models and Tesseract both degrade on oversized, cluttered, or
low-contrast input — and both fail *silently*, returning confident-looking
garbage. Thirty seconds of preprocessing routinely turns a failed extraction
into a clean one. Prep is the retry strategy for image reading, applied
*before* concluding "the image is unreadable".

## Usage — `scripts/prep.py`

Subcommand first, then the file. Every command applies EXIF orientation
before touching geometry, and outputs PNG end-to-end:

```bash
python scripts/prep.py thumb     shot.png --max 1568          # aspect-preserving downscale
python scripts/prep.py crop      shot.png --box 100,80,700,420  # the dialog that matters
python scripts/prep.py split     dash.png --grid 2,3          # six panels → panel_N.png
python scripts/prep.py contrast  faint.png --ocr              # grayscale+autocontrast (+2x for OCR)
python scripts/prep.py deskew    scan.png  --angle -1.5       # white fill, expand
```

`--ocr` lane = the recipe Tesseract wants (grayscale → autocontrast → 2×
LANCZOS); vision lane = `thumb` only, never upscale (vision resizes
internally — upscaling just inflates payload).

## Recipes → commands

- **Downscale monsters** (>2000px): vision resamples them tile-blurry; LANCZOS
  thumbnail keeps text crisp where default resampling smears.
- **Crop to the subject:** signal-per-pixel is the metric — the model spends
  attention on everything visible. Crop coordinates come from a cheap probe
  (read the image small/whole first), never blind box math.
- **Split multi-panel captures:** one read of N panels blends them; N reads of
  one panel each stay attributed.
- **Contrast for faint text:** gray-on-gray themes and low-quality photos.
- **Deskew photographed pages:** even ±2° breaks OCR line detection.

## Gotchas

- **EXIF orientation strikes before everything**: phone photos open sideways
  in Pillow; transpose FIRST, or every crop box targets the wrong region
  (the script does it; hand-rolled Pillow must too).
- **Never OCR a JPEG re-save of a screenshot**: compression ringing around
  glyph edges is exactly what Tesseract trips on. Keep screenshots PNG
  end-to-end; work from the original, don't "clean up" a JPEG copy.
- **Upscaling helps OCR, wastes vision** — route-specific prep, not one pipeline.
- **Prep is escalation, not default**: a clean 1200px screenshot needs nothing
  here; run the reader first, prep on failure.

## Boundaries

Reading the prepped result: `read-image` (structured content), `image-ocr`
(verbatim bulk text — its `--prep` flag runs the contrast lane itself) — this
skill feeds both, extracts nothing itself. General-purpose manipulation
(thumbnails for delivery, watermarks, format conversion) → `image`.
Text-format diagram files (.mmd, .puml, SVG source) never need prep →
`read-diagram` directly.
