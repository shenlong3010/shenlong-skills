---
name: data-csv
description: Read, clean, and write CSV/tabular data with pandas (and stdlib csv for streaming) — dtype control, encodings, big files, datetime parsing. Use for "parse this CSV", "clean this data", "combine these files", or any tabular file wrangling where the deliverable is data, not a spreadsheet.
derivation: original
flow: util
domain: data
---

# data-csv

```bash
pip install pandas
```

## Read correctly (where most bugs enter)

```python
import pandas as pd
df = pd.read_csv("in.csv",
    dtype={"zip": "string", "account_id": "string"},  # else 02134 -> 2134
    parse_dates=["created_at"],
    encoding="utf-8-sig",        # eats the Excel BOM; try cp1252 for legacy exports
    na_values=["", "NULL", "N/A"])
```

- **dtype inference is the classic corruption:** leading-zero codes become ints, long ids become floats with precision loss (`1234567890123456789 -> 1.2345678901234568e+18`). Declare `dtype=` for every identifier column.
- Huge files: `chunksize=100_000` returns an iterator — aggregate per chunk; or `usecols=` to load only needed columns.
- `low_memory` warning = mixed types detected in a column — that's a data-quality finding, not noise; inspect it.

## Write

```python
df.to_csv("out.csv", index=False)     # index=False or you ship a junk first column
```

Excel-bound output: `encoding="utf-8-sig"` so Excel detects UTF-8.

## Streaming without pandas
Appending rows in a long loop: stdlib `csv.writer` on an open file beats rebuilding DataFrames. `newline=""` in `open()` on Windows or you get blank lines.

## Gotchas
- Merge key dtypes must match (`"7" != 7`): pandas 3+ raises `ValueError: You are trying to merge on str and int64 columns` (verified 3.0.3); pandas <3 silently returned an empty join. Either way, normalize dtypes before `df.merge`.
- `df[df.col == x]` on a column pandas parsed as float never equals your int — back to dtype discipline.
- Dates without `parse_dates` are strings; sorting them sorts lexically.
