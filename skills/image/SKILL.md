---
name: image
description: Manipulate images with Pillow — resize, convert, crop, compose, thumbnails, EXIF orientation, format conversion. Use for "resize these images", "convert PNG to JPEG", "make thumbnails", "watermark this image", or any raster processing. For extracting text from images use image-ocr; for describing content, native vision.
derivation: original
flow: util
---

# image

```bash
pip install Pillow
```

## The two traps first

```python
from PIL import Image, ImageOps

im = Image.open("photo.jpg")
im = ImageOps.exif_transpose(im)     # 1) phones store rotation in EXIF —
                                     #    skip this and portraits come out sideways
im.convert("RGB").save("out.jpg")    # 2) RGBA/P -> JPEG raises; convert first
```

## Core operations

```python
im.thumbnail((800, 800))                         # in-place, KEEPS aspect ratio
small = im.resize((800, 600))                    # exact size, distorts if ratio differs
box = im.crop((left, top, right, bottom))
im.save("out.jpg", quality=85, optimize=True)    # 85 = sane web default
im.save("out.webp")                              # format from extension
```

Compositing / watermark:

```python
base = Image.open("base.png").convert("RGBA")
mark = Image.open("logo.png").convert("RGBA")
base.paste(mark, (x, y), mask=mark)              # mask=itself -> respects alpha
base.convert("RGB").save("out.jpg")
```

Text: `ImageDraw.Draw(im).text((x, y), "hi", font=ImageFont.truetype("DejaVuSans.ttf", 24))` — default bitmap font is tiny and unscalable; always load a truetype.

## Gotchas
- `Image.open` is lazy — the file handle lives until `.load()`/context exit; in loops use `with Image.open(p) as im:` or you leak fds.
- `thumbnail` mutates and returns None; `resize` returns new — mixing the two idioms produces `NoneType` errors.
- Pixel access via `im.getpixel` in loops is slow — use numpy (`np.asarray(im)`) for per-pixel math.
- Batch: build once, `im.close()` or context-manage; PIL caches decoders per image.
