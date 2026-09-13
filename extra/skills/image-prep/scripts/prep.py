#!/usr/bin/env python3
"""Prep CLI for the image-prep skill — Pillow preprocessing before vision/OCR.

Subcommands (EXIF orientation is applied first, always):
    thumb   IN --max N [--out P]      aspect-preserving downscale (LANCZOS)
    crop    IN --box L,T,R,B [--out]  crop to the region that matters
    split   IN --grid COLS,ROWS [--outdir D]  cut multi-panel captures into panels
    contrast IN [--ocr] [--out P]      grayscale + autocontrast; --ocr adds 2x LANCZOS
    deskew  IN --angle DEG [--out P]  rotate with white fill, expand

Output defaults to <input>-prep.png beside the input (split writes panel_N.png
files to --outdir, default <input>-panels/). PNG end-to-end — never re-save a
screenshot as JPEG (the ringing law).

Requires: pip install pillow.  Exit codes: 0 ok · 2 usage/IO error.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(2)


def open_fixed(path):
    with Image.open(path) as src:
        return ImageOps.exif_transpose(src).copy()


def out_path(inp, suffix="-prep"):
    p = Path(inp)
    return p.with_name(f"{p.stem}{suffix}.png")


def save_png(img, path):
    img.save(path, format="PNG")
    print(f"{path}  ({img.width}x{img.height}, {img.mode})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("thumb", help="aspect-preserving downscale")
    p.add_argument("input"); p.add_argument("--max", type=int, default=1568); p.add_argument("--out")

    p = sub.add_parser("crop", help="crop to L,T,R,B")
    p.add_argument("input"); p.add_argument("--box", required=True); p.add_argument("--out")

    p = sub.add_parser("split", help="split into COLSxROWS panels")
    p.add_argument("input"); p.add_argument("--grid", required=True); p.add_argument("--outdir")

    p = sub.add_parser("contrast", help="grayscale+autocontrast (OCR lane: +2x upscale)")
    p.add_argument("input"); p.add_argument("--ocr", action="store_true"); p.add_argument("--out")

    p = sub.add_parser("deskew", help="rotate by --angle degrees")
    p.add_argument("input"); p.add_argument("--angle", type=float, required=True); p.add_argument("--out")

    args = ap.parse_args(argv)
    try:
        img = open_fixed(args.input)
    except (FileNotFoundError, OSError) as exc:
        fail(f"cannot open {args.input}: {exc}")

    if args.cmd == "thumb":
        if img.width <= args.max and img.height <= args.max:
            print(f"{args.input} already within {args.max}px — no-op")
            return 0
        img.thumbnail((args.max, args.max), Image.LANCZOS)
        save_png(img, Path(args.out) if args.out else out_path(args.input))

    elif args.cmd == "crop":
        try:
            box = tuple(int(v) for v in args.box.split(","))
            assert len(box) == 4
        except (ValueError, AssertionError):
            fail("--box wants L,T,R,B integers")
        if not (0 <= box[0] < box[2] <= img.width and 0 <= box[1] < box[3] <= img.height):
            fail(f"--box {box} outside image {img.size}")
        save_png(img.crop(box), Path(args.out) if args.out else out_path(args.input, "-crop"))

    elif args.cmd == "split":
        try:
            cols, rows = (int(v) for v in args.grid.split(","))
            assert cols > 0 and rows > 0
        except (ValueError, AssertionError):
            fail("--grid wants COLS,ROWS integers")
        outdir = Path(args.outdir) if args.outdir else Path(out_path(args.input, "-panels"))
        outdir.mkdir(parents=True, exist_ok=True)
        w, h = img.width // cols, img.height // rows
        n = 0
        for r in range(rows):
            for c in range(cols):
                panel = img.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))
                save_png(panel, outdir / f"panel_{n}.png")
                n += 1

    elif args.cmd == "contrast":
        out = ImageOps.autocontrast(img.convert("L"))
        if args.ocr:
            out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
        save_png(out, Path(args.out) if args.out else out_path(args.input, "-contrast"))

    elif args.cmd == "deskew":
        save_png(img.rotate(args.angle, expand=True, fillcolor="white"),
                 Path(args.out) if args.out else out_path(args.input, "-deskew"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
