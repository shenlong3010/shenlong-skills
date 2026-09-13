#!/usr/bin/env python3
"""OCR CLI for the image-ocr skill — Tesseract via pytesseract.

Extracts text from images (JPG/JPEG/PNG/WEBP) and emits the skill's JSON
schema, one object per image. Single file or batch directory.

Usage:
    python ocr.py <image-or-dir> [--lang eng] [--psm N] [--out results.json]
                  [--min-conf HIGH] [--prep]

    --lang     Tesseract language packs, '+'-joined (default: eng)
    --psm      page segmentation mode 0-13 (default: 3; 6 for uniform blocks,
               11 for sparse text — see SKILL.md table)
    --out      also write the JSON array to this file
    --min-conf average-confidence threshold for "high" (default 80)
    --prep     apply the OCR prep lane (grayscale + autocontrast + 2x LANCZOS
               upscale) before extraction — the image-prep recipe

Requires: pip install pytesseract pillow  AND the native Tesseract binary
(Windows: winget install UB-Mannheim.TesseractInstaller, then PATH or
pytesseract.pytesseract.tesseract_cmd — see SKILL.md).

Exit codes: 0 all images processed · 1 one or more extractions failed ·
2 environment/usage error (Tesseract missing, no images found).
"""

import argparse
import json
import sys
from pathlib import Path

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def fail(msg, code=2):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_image(path, prep):
    from PIL import Image, ImageOps

    with Image.open(path) as src:
        img = ImageOps.exif_transpose(src).copy()   # EXIF first — sideways crops lie
    if prep:
        img = ImageOps.autocontrast(img.convert("L"))
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img


def ocr_one(path, lang, psm, min_conf, prep):
    import pytesseract

    result = {
        "success": False,
        "filename": Path(path).name,
        "extracted_text": "",
        "confidence": "low",
        "metadata": {"language_detected": lang, "text_regions": 0,
                     "has_tables": False, "has_handwriting": False},
        "warnings": [],
    }
    try:
        img = load_image(path, prep)
        config = f"--psm {psm}" if psm != 3 else ""
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        data = pytesseract.image_to_data(img, lang=lang, config=config,
                                         output_type=pytesseract.Output.DICT)
    except Exception as exc:                       # noqa: BLE001 — schema requires the error in-band
        result["warnings"].append(f"OCR failed: {exc}")
        return result

    confs = [c for c in data["conf"] if isinstance(c, (int, float)) and c > 0]
    avg = sum(confs) / len(confs) if confs else 0.0
    words = [w for w in data["text"] if w.strip()]
    regions = {b for b in data["block_num"] if b > 0}

    result["extracted_text"] = text.strip()
    result["success"] = True
    result["metadata"]["text_regions"] = len(regions)
    if avg >= min_conf:
        result["confidence"] = "high"
    elif avg >= 50:
        result["confidence"] = "medium"
    else:
        result["confidence"] = "low"
        result["warnings"].append(f"low OCR confidence: {avg:.1f}% — "
                                  f"retry with --prep, a higher --psm, or image-prep first")
    if not words:
        result["warnings"].append("no text detected")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="image files or directories")
    ap.add_argument("--lang", default="eng")
    ap.add_argument("--psm", type=int, default=3, choices=range(0, 14))
    ap.add_argument("--out")
    ap.add_argument("--min-conf", type=int, default=80)
    ap.add_argument("--prep", action="store_true")
    args = ap.parse_args(argv)

    try:
        import pytesseract  # noqa: F401
    except ImportError:
        fail("pytesseract not installed — pip install pytesseract pillow")

    import pytesseract
    try:
        pytesseract.get_tesseract_version()
    except Exception:                              # noqa: BLE001 — wrapper present, binary missing
        fail("Tesseract binary not found — install it "
             "(Windows: winget install UB-Mannheim.TesseractInstaller, then add its "
             "dir to PATH or set pytesseract.pytesseract.tesseract_cmd; "
             "macOS: brew install tesseract; Debian/Ubuntu: apt install tesseract-ocr)")

    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(f for f in path.iterdir()
                                if f.suffix.lower() in EXTENSIONS))
        elif path.suffix.lower() in EXTENSIONS:
            files.append(path)
        else:
            fail(f"not a readable image type: {path}")
    if not files:
        fail("no images found in the given path(s)")

    results = [ocr_one(f, args.lang, args.psm, args.min_conf, args.prep)
               for f in files]
    for r in results:
        print(json.dumps(r, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if all(r["success"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
