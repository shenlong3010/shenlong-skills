---
name: image-prep
description: Preprocess images before vision or OCR — downscale huge screenshots, crop to the region that matters, split multi-panel captures, boost contrast for faint text. Use when an image is >2000px on a side, a screenshot contains many windows/panels but one matters, OCR returns garbage on readable-looking text, or a diagram photo is skewed/dim — prep first, then re-run the read.
derivation: original
flow: lookup
domain: media
---

# Image Prep

## Purpose
Vision models and Tesseract both degrade on oversized, cluttered, or low-contrast input — and both fail *silently*, returning confident-looking garbage. Thirty seconds of Pillow preprocessing routinely turns a failed extraction into a clean one. Prep is the retry strategy for image reading, applied *before* concluding "the image is unreadable".

## Recipes (Pillow — the `image` skill owns general manipulation; these are the extraction-serving cases)

- **Downscale monsters**: >2000px on a side gets resampled tile-blurry by vision. `img.thumbnail((1568, 1568), Image.LANCZOS)` preserves aspect; text stays crisp at LANCZOS where default resampling smears it.
- **Crop to the subject**: a full-desktop screenshot where one dialog matters → crop the dialog region, read the crop. Signal-per-pixel is the metric; the model spends attention on everything visible.
- **Split multi-panel captures**: side-by-side terminals, before/after pairs, grid dashboards → `img.crop(box)` per panel, read each separately. One read of N panels blends them; N reads of one panel each stay attributed.
- **Contrast for faint text**: gray-on-gray terminal themes, low-quality photos → `ImageOps.autocontrast(img.convert("L"))`; for OCR add 2× upscale (`img.resize((w*2, h*2), Image.LANCZOS)`) — Tesseract wants ~300 DPI-equivalent, and small UI text is far below it.
- **Deskew photographed documents/whiteboards**: small rotations kill OCR line detection — `img.rotate(angle, expand=True, fillcolor="white")`; even eyeballed ±2° correction measurably improves it.

## Gotchas
- **EXIF orientation strikes before everything**: phone photos open sideways in Pillow; `ImageOps.exif_transpose(img)` FIRST, or every crop box targets the wrong region.
- **Never OCR a JPEG re-save of a screenshot**: JPEG ringing around glyph edges is exactly what Tesseract trips on. Keep screenshots PNG end-to-end; if handed a JPEG, don't "clean it up" by re-saving — work from the original.
- **Upscaling helps OCR, wastes vision**: 2× LANCZOS measurably lifts Tesseract on small text; vision models resize internally, so upscaling for them only inflates payload. Route-specific prep, not one pipeline.
- **Crop coordinates come from a cheap probe, not guesses**: read the image once small/whole to locate the region, then crop precisely — blind box math on an unseen image produces beautifully prepped noise.

## Boundaries
Reading the prepped result: `read-image` (structured content), `image-ocr` (verbatim bulk text) — this skill feeds both, extracts nothing itself. General-purpose manipulation (thumbnails, watermarks, format conversion for delivery) → `image`. Text-format diagram files (.mmd, .puml, SVG source) never need prep → `read-diagram` directly.
