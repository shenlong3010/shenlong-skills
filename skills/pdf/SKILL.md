---
name: pdf
description: Read, merge, split, fill, and create PDFs with pypdf and reportlab — text extraction, page ops, form filling, watermarks, generated documents. Use whenever a PDF must be parsed, assembled, or produced by script, or when asked for a ".pdf" deliverable, "merge these PDFs", "extract text from this PDF", "fill this form". For scanned/image PDFs route text extraction to the image-ocr skill.
derivation: original
---

# pdf — PDFs via pypdf + reportlab

```bash
pip install pypdf reportlab
```

## Read / extract (pypdf)

```python
from pypdf import PdfReader
r = PdfReader("in.pdf")
text = "\n".join(page.extract_text() or "" for page in r.pages)
```

- Extraction is layout-lossy by design (reading order ≈ content-stream order; columns and tables scramble). For tables, use `pdfplumber` instead.
- **Empty text ⇒ scanned/image PDF** — no text layer exists. Rasterize pages (`pypdfium2` or `pdf2image`) and route to the **image-ocr** skill; do not report "no text found" as if the document were empty.

## Page ops (pypdf)

```python
from pypdf import PdfReader, PdfWriter
w = PdfWriter()
for src in ("a.pdf", "b.pdf"):
    for p in PdfReader(src).pages: w.add_page(p)      # merge
w.add_page(PdfReader("c.pdf").pages[0])               # split = pick pages
w.pages[0].rotate(90)
with open("out.pdf", "wb") as f: w.write(f)
```

Watermark/stamp: `page.merge_page(stamp_page)`. Encrypt: `w.encrypt("userpw")`; decrypt: `PdfReader(p, password=...)`.

## Forms (pypdf)

```python
r = PdfReader("form.pdf"); w = PdfWriter(clone_from=r)
print(r.get_fields().keys())                          # discover exact field names first
w.update_page_form_field_values(w.pages[0], {"name": "Luke", "amount": "1200"},
                                auto_regenerate=False)
```

- Filled values invisible in some viewers → set **NeedAppearances**: `w.set_need_appearances_writer(True)` (or the AcroForm dict tweak on older versions). This quirk is the #1 form-fill bug.
- XFA forms (LiveCycle) are not AcroForms — pypdf can't fill them; detect via `/XFA` and say so.

## Create (reportlab)

```python
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
c = canvas.Canvas("new.pdf", pagesize=LETTER)
w_pt, h_pt = LETTER                                   # origin = BOTTOM-left, y grows up
c.setFont("Helvetica-Bold", 16); c.drawString(72, h_pt - 72, "Invoice #42")
c.line(72, h_pt - 80, w_pt - 72, h_pt - 80)
c.showPage(); c.save()
```

- Coordinate origin bottom-left trips everyone once — compute y as `height - offset`.
- Flowing documents (paragraphs, tables, page breaks): use `reportlab.platypus` (`SimpleDocTemplate`, `Paragraph`, `Table`) instead of raw canvas.
- Page numbers: draw in an `onPage` callback passed to the doc template.
