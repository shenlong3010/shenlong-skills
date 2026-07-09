---
name: docx
description: Create and edit Word documents (.docx) programmatically with python-docx — headings, styled paragraphs, tables, images, headers/footers, find-and-replace. Use whenever a Word document must be generated or modified by script — reports, memos, letters, template filling — or when asked for a ".docx", "Word doc", or document deliverable. Committable open-source baseline; for tracked changes, comments, or deep OOXML surgery use the vendored Anthropic docx skill (vendor/anthropic, local fetch) instead.
derivation: original
---

# docx — Word documents via python-docx

```bash
pip install python-docx
```

## Quickstart

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor

doc = Document()                      # or Document("template.docx")
doc.add_heading("Quarterly Report", level=1)
p = doc.add_paragraph("Revenue grew ")
run = p.add_run("18%")                # runs = formatting boundaries
run.bold = True
doc.add_picture("chart.png", width=Inches(5.5))

table = doc.add_table(rows=1, cols=3)
table.style = "Light Grid Accent 1"
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "Region", "Q1", "Q2"
for region, q1, q2 in data:
    c = table.add_row().cells
    c[0].text, c[1].text, c[2].text = region, str(q1), str(q2)

doc.save("report.docx")               # overwrites silently
```

## Core operations
- **Styles:** `doc.add_paragraph("x", style="Quote")` — the style must already exist in the document/template or python-docx raises `KeyError`. For branded output, start from a `.docx` template that defines the styles.
- **Sections / layout:** `section = doc.sections[0]`; orientation via `section.orientation` + swapping `page_width`/`page_height`; margins via `section.left_margin = Inches(1)`.
- **Headers/footers:** `section.header.paragraphs[0].text = "Confidential"`.
- **Page break:** `doc.add_page_break()`.

## Gotchas (the ones that burn time)
- **Find-and-replace across runs:** Word splits text into runs unpredictably (spellcheck, formatting history), so `"{{name}}"` may span 3 runs and naive `run.text.replace` misses it. Either replace at `paragraph.text` level (loses intra-paragraph formatting) or iterate runs and rebuild. For heavy templating use `docxtpl` (Jinja in Word) instead of hand-rolling.
- **`data_only` doesn't exist here** — that's openpyxl. python-docx has no field-code evaluation; TOC fields need a manual "update fields" on open (or set the update-on-open flag via XML).
- **Legacy `.doc` (binary) unsupported** — convert with LibreOffice headless first: `soffice --headless --convert-to docx file.doc`.
- **Tracked changes / comments:** not supported by python-docx — do not fake it; route to the proprietary skill or manual editing.
- Reading: `Document(path)` then walk `doc.paragraphs` and `doc.tables`; text inside text-boxes/shapes is NOT in `doc.paragraphs` (lives in deeper XML).
