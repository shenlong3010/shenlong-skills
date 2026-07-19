---
name: xlsx
description: Create, read, and edit Excel workbooks (.xlsx) with openpyxl — formulas, number formats, styling, charts, freeze panes, large-file modes. Use whenever a spreadsheet must be generated, parsed, or modified by script, or when asked for an ".xlsx", "Excel file", "spreadsheet", or tabular deliverable. Pairs with pandas for bulk data. Committable open-source baseline.
derivation: original
flow: deliver
domain: docs
---

# xlsx — Excel via openpyxl

```bash
pip install openpyxl            # + pandas for bulk data
```

## Quickstart

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Summary"
ws.append(["Region", "Revenue", "Target", "Delta"])          # row 1
for r, (region, rev, tgt) in enumerate(rows, start=2):
    ws.cell(row=r, column=1, value=region)                    # 1-indexed!
    ws.cell(row=r, column=2, value=rev)
    ws.cell(row=r, column=3, value=tgt)
    ws.cell(row=r, column=4, value=f"=B{r}-C{r}")             # formula = string
ws["B2:D100"]  # ranges work; style header:
for c in ws[1]:
    c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="DDDDDD")
ws.freeze_panes = "A2"
ws.column_dimensions["A"].width = 18
wb.save("report.xlsx")
```

## Core operations
- **Number formats:** `cell.number_format = "#,##0.00"`, dates `"yyyy-mm-dd"`, percents `"0.0%"` — a float with a percent format is the Excel-native way (0.18 → 18.0%).
- **Charts:** `from openpyxl.chart import BarChart, Reference`; build `Reference(ws, min_col=…, min_row=…)`, `chart.add_data(..., titles_from_data=True)`, `ws.add_chart(chart, "F2")`.
- **Reading:** `load_workbook(path, data_only=True)` returns *cached* formula results — present only if Excel saved the file; a workbook written by openpyxl and never opened in Excel has `None` there. openpyxl **never computes formulas**.
- **Bulk data:** `pd.read_excel(path, engine="openpyxl")` / `df.to_excel(...)`; use openpyxl directly only for formatting on top.

## Gotchas
- **1-indexed everywhere** — `ws.cell(row=1, column=1)` is A1; off-by-one from pandas habits is the #1 bug.
- **Merged cells:** only the top-left cell holds the value; the rest read `None`. Unmerge or check `ws.merged_cells.ranges` before iterating.
- **Large files:** `read_only=True` / `write_only=True` modes stream instead of loading everything; write-only requires append-style building (no random cell access).
- **.xls (legacy)** unsupported — convert first or use `xlrd<2.0` read-only.
- Column letters ↔ numbers: `get_column_letter(n)` / `column_index_from_string("AB")` — don't hand-roll base-26.
