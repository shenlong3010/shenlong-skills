---
name: pptx
description: Build and edit PowerPoint decks (.pptx) with python-pptx — slides, layouts, placeholders, text formatting, images, tables, speaker notes. Use whenever slides or a deck must be generated or modified by script, or when asked for a ".pptx", "presentation", "slide deck", or "slides" deliverable. Committable open-source baseline; start from a branded template for corporate output.
derivation: original
flow: deliver
domain: docs
---

# pptx — PowerPoint via python-pptx

```bash
pip install python-pptx
```

## Quickstart

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()                          # or Presentation("brand.pptx")
title_layout = prs.slide_layouts[0]           # layout indices are TEMPLATE-SPECIFIC
slide = prs.slides.add_slide(title_layout)
slide.shapes.title.text = "Harness Engineering"
slide.placeholders[1].text = "Q3 review"

blank = prs.slide_layouts[6]                  # 6 = blank in the DEFAULT template only
s2 = prs.slides.add_slide(blank)
box = s2.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(8), Inches(1.2))
tf = box.text_frame
tf.text = "Key results"
para = tf.add_paragraph(); para.text = "Token spend down"; para.level = 1
para.runs[0].font.size = Pt(20); para.runs[0].font.bold = True
s2.shapes.add_picture("chart.png", Inches(1), Inches(2.2), width=Inches(7))

prs.save("deck.pptx")
```

## Core operations
- **Inspect a template first:** layout indices and placeholder `idx` values differ per template. Loop `for i, l in enumerate(prs.slide_layouts): print(i, l.name)` and `for ph in slide.placeholders: print(ph.placeholder_format.idx, ph.name)` before assuming anything.
- **16:9:** default template is already widescreen in recent versions; otherwise `prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)`.
- **Tables:** `shapes.add_table(rows, cols, left, top, width, height).table`; cell text via `table.cell(r, c).text`.
- **Speaker notes:** `slide.notes_slide.notes_text_frame.text = "..."`.

## Gotchas
- **Copying a slide between decks is not supported natively** — it requires deep XML cloning of the slide part + related media; say so instead of pretending, or restructure to regenerate the slide in the target deck.
- **Text autofit** doesn't recompute font sizes on save — overset text overflows silently; size text yourself or keep content within known bounds.
- **Charts:** python-pptx can create basic chart types (`add_chart` with `CategoryChartData`), but complex styling is limited — for polished charts, render with matplotlib → `add_picture`.
- Bullets come from the layout's list styles; `paragraph.level` sets indent level, it does not invent bullet glyphs on a bare textbox.
