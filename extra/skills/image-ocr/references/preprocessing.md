# Preprocessing strategies for hard images

Escalation ladder for images where plain OCR returns garbage or low confidence.
Each step is one Pillow transform; apply, re-run `scripts/ocr.py`, and stop at
the first pass — over-processed images OCR *worse* (thresholding a clean scan
destroys antialiasing it needed).

Verified with Pillow 12.x on Windows; API-stable operations only.

## 1. Grayscale + autocontrast (try first)

```python
from PIL import Image, ImageOps
img = ImageOps.autocontrast(Image.open(p).convert("L"))
```

Fixes gray-on-gray terminal themes and washed-out photos. `convert("L")` drops
color channels Tesseract ignores anyway; autocontrast stretches the histogram
to full range. Equivalent: `ocr.py --prep`.

## 2. Invert dark backgrounds

```python
from PIL import Image, ImageOps
img = ImageOps.invert(Image.open(p).convert("L"))
```

Tesseract's models are trained predominantly on dark-text-on-light. Light
text on dark background (dark IDE themes, terminals) often jumps from garbage
to clean after inversion. If unsure, run both and keep the higher confidence.

## 3. Upscale small text 2–3×

```python
img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
```

Tesseract wants ~300 DPI-equivalent glyphs; screenshots at 100% zoom are far
below that. LANCZOS, never NEAREST — blocky edges are new noise. Included in
`ocr.py --prep`. Beyond 3× returns diminish and payload grows.

## 4. Threshold only for true bilevel sources

```python
img = img.point(lambda v: 255 if v > 160 else 0)
```

For photos of paper with shadow gradients, binarization can separate text from
background. The cutoff is image-specific — 160 is a starting guess, sweep
120–190. Skip for screenshots and UI captures: their antialiasing is signal,
and thresholding converts smooth glyph edges into jagged ones Tesseract reads
worse. If you need this on a screenshot, the real problem is usually contrast
(step 1) or scale (step 3).

## 5. Deskew photographed pages

```python
img = img.rotate(angle_degrees, expand=True, fillcolor="white")
```

Even ±2° of skew breaks Tesseract's line-finding on dense text. Small angles:
estimate by eye against a horizontal ruler on screen, or compute via
`pytesseract.image_to_osd` for orientation (90° rotations, not fine skew).
`expand=True` prevents corner clipping; white fill matches paper.

## Order of operations

exif_transpose **always first** (sideways images make every later box wrong —
the `image-prep` EXIF law) → deskew → invert (if dark bg) → grayscale +
autocontrast → upscale → threshold (last resort).

## Cross-references

- `image-prep` owns the general prep recipes and the JPEG-re-save law: never
  OCR a re-saved JPEG screenshot — work from the original PNG.
- `read-image` routes here: dense text regions in screenshots are bulk-verbatim
  extraction, not vision retyping.
