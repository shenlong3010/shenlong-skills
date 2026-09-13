---
name: image-ocr
description: Extract text from images (JPG, PNG, WEBP) deterministically using Tesseract OCR via pytesseract, returning structured JSON. Use for scanned documents, screenshots with dense text, receipts, forms, photos of text, or batch image-to-text extraction — whenever exact machine-readable verbatim output is needed rather than a visual description. Do NOT use for describing or reasoning about image content (`read-image`) or text-format diagram files (`read-diagram`).
derivation: adapted
source: https://github.com/benchflow-ai/skillsbench/tree/main/tasks/jpg-ocr-stat/environment/skills/image-ocr
license: Apache-2.0 (upstream benchflow-ai/skillsbench)
flow: lookup
domain: media
---

# Image OCR

Deterministic, verbatim text extraction — the complement to vision: vision
describes and reasons; this skill transcribes exactly, with confidence scores.

## Install (both layers are required)

`pip install pytesseract pillow` installs the *wrapper only* — without the
native binary every call raises `TesseractNotFoundError`:

- **Windows:** `winget install UB-Mannheim.TesseractInstaller`, then add its
  dir to PATH or set `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`.
- **macOS:** `brew install tesseract` · **Debian/Ubuntu:** `sudo apt install tesseract-ocr`

Verify before relying on it: `pytesseract.get_tesseract_version()`.

## Usage — `scripts/ocr.py`

The script implements the output schema below; don't retype the boilerplate:

```bash
python scripts/ocr.py screenshot.png                       # one image → JSON
python scripts/ocr.py scans/ --out results.json            # batch a directory
python scripts/ocr.py faint.png --prep                     # grayscale+autocontrast+2x upscale first
python scripts/ocr.py form.png --psm 6 --lang eng+fra      # uniform block, multilingual
```

Exit codes: 0 clean · 1 an extraction failed · 2 environment error (binary
missing — the message carries the install lane).

## Output schema

```json
{
  "success": true,
  "filename": "example.jpg",
  "extracted_text": "Full raw text in reading order...",
  "confidence": "high|medium|low",
  "metadata": { "language_detected": "en", "text_regions": 3,
                "has_tables": false, "has_handwriting": false },
  "warnings": ["low OCR confidence: 42.1% — retry with --prep..."]
}
```

`confidence` is the mean per-word score from `image_to_data`: high ≥ 80,
medium ≥ 50, low below. A `low` result is a *prep signal*, not a final answer —
escalate through `references/preprocessing.md` before concluding the image is
unreadable.

## Page segmentation modes (`--psm`)

| PSM | Use for |
|-----|---------|
| 3 | default — full automatic page segmentation |
| 4 | single column, variable line sizes |
| 6 | uniform block of text (screenshots of code/config) |
| 7 | single text line |
| 11 | sparse text — find as much as possible (UI labels scattered on a canvas) |
| 13 | raw line, no Tesseract-side layout logic |

Wrong PSM is the #1 cause of "readable-looking text, garbage output": a dense
screenshot under PSM 11 hallucinates order; scattered UI text under PSM 3
returns nothing. When confidence is low, sweep PSM before touching the image.

## Gotchas

- **EXIF orientation first** (`ImageOps.exif_transpose`) — sideways input
  silently degrades every downstream number (the `image-prep` law; the script does it).
- **Never OCR a re-saved JPEG screenshot** — compression ringing around glyphs
  is exactly what Tesseract trips on; work from the original PNG (`image-prep`).
- **DPI beats cleverness:** small UI text wants the 2× LANCZOS upscale more
  than any filter (`--prep` includes it).
- **Language packs are separate installs** — `--lang deu` fails until the
  `tesseract-ocr-deu` pack is installed; the error names the missing pack.

## Boundaries

- Describing/reasoning about image content → `read-image` (routes dense text
  regions here — that split is: vision for meaning, this for verbatim).
- Preprocessing beyond the built-in `--prep` (crop, split panels, deskew) →
  `image-prep`, then re-run this skill.
- Text-format diagram files (.mmd/.puml/.svg) → `read-diagram` — they parse as
  text; OCR on them is a lossy round trip.
