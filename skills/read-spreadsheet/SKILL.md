---
name: read-spreadsheet
description: Comprehend a human-built spreadsheet — .xlsx, .xls, .ods, Google Sheets export — where meaning is smeared across merged cells, multiple tables per sheet, header rows that aren't row 1, colour-coded status, and notes-in-cells, into the actual data and what it means. Use whenever a real-world spreadsheet's content must be understood — "what's in this spreadsheet", "pull the numbers from this sheet", "what does this workbook track", "which rows are flagged", "reconcile these two sheets". Do NOT use for mechanically writing/parsing a clean spreadsheet (that is the xlsx skill) or for a tidy single-table CSV (that is data-csv).
derivation: original
flow: lookup
domain: data
---

# Read Spreadsheet

Turn a spreadsheet a human built for other humans into structured data and its meaning — finding the real tables inside the mess, not assuming row 1 is headers and every cell is data.

## Scope boundary

`xlsx` writes and mechanically parses workbooks; `data-csv` handles a clean, tidy single-table CSV with pandas. This skill is for the *untidy real-world sheet*: merged cells, several tables stacked on one sheet, a title banner and notes above the real header, colour/format carrying meaning, subtotal rows mixed with data, cross-sheet references. When the sheet is already tidy (one table, headers in row 1, one value per cell), skip this and use `data-csv`/`xlsx` directly.

## Output: the sheet brief

- **Workbook map** — sheets that matter and what each holds; ignore scratch/hidden/legend sheets after noting they exist.
- **Table regions** — for each real table on a sheet: its cell range, where the header row actually is, and one line on what it holds. A sheet often has 2–3 tables separated by blank rows; each is a separate region.
- **Column meaning** — the real meaning of each column, resolving merged/multi-row headers into single names, and flagging any column whose values disagree with its header (a "Date" column holding text like "Q3").
- **Encoded-in-format meaning** — status carried by cell colour, bold, or strikethrough; notes/comments attached to cells; these carry data that a values-only read silently drops.
- **Derived vs source rows** — which rows are subtotals/totals/formulas vs raw data. Summing a column that already contains its own subtotal double-counts.
- **Anomalies** — text in numeric columns, mixed date formats, hidden rows/columns, `#REF!`/`#DIV/0!` errors, values that are formulas pointing off-sheet.

Answer the user's actual question from this brief; emit the full map for "what's in this workbook".

## Reading procedure

1. **Survey structure before values.** Open with a tool that exposes cells positionally (`openpyxl` — the `xlsx` skill's engine — not pandas' assume-a-table read). Find where data actually starts; the top rows are usually a title, a date, a legend.
2. **Detect the header row, don't assume it.** The header is the first row where cells are labels for the columns below, often row 3–5. Merged cells spanning columns are group headers *above* the real headers — flatten them into `group / sub` names.
3. **Segment into table regions.** Blank rows/columns and a fresh header row mark a new table. Treat each region independently; never read a whole sheet as one dataframe when it holds three tables.
4. **Read format where format is data.** Pull cell fill colour, font style, and cell comments when status appears encoded that way — `openpyxl` exposes `.fill`, `.font`, `.comment`. A read that only takes `.value` loses the meaning of the colour column.
5. **Separate source from derived.** Flag rows whose cells are formulas (subtotals, running totals) and rows labelled Total/Subtotal, so aggregation uses source rows only.

## Gotchas

- **Row 1 is rarely the header.** Human sheets open with a title banner, a "last updated" line, or a company logo row. Assuming row 1 = headers shifts every column name by one and silently corrupts the whole read. Detect the header row.
- **Merged cells hold their value only in the top-left.** In a merged range, `openpyxl` returns the value for the anchor cell and `None` for the rest. A group label merged across five columns reads as one label + four blanks — forward-fill it, don't treat the blanks as missing data.
- **Format carries data the values don't.** Red fill = overdue, strikethrough = cancelled, a cell comment = the real explanation. A values-only extraction (especially CSV export) drops all of it. If the task is about status, you must read format.
- **Subtotal rows poison aggregation.** A column with per-row values *and* a subtotal row sums to double. Identify and exclude derived rows before any total.
- **Numbers that are text (and vice versa).** Leading-apostrophe numbers, numbers stored as strings, dates stored as text or as Excel serial integers (45000-ish). Check dtype per column; a "sum" over text silently yields 0 or concatenation.
- **CSV export throws away everything but values.** Merges, colours, comments, formulas, multiple sheets, and hidden rows all vanish when someone "just export to CSV". If those carry meaning, read the .xlsx, not its CSV shadow.
- **The .xls vs .xlsx trap.** Legacy `.xls` is a different binary format; `openpyxl` reads only `.xlsx`/`.xlsm`. For `.xls` use a converter or a reader that supports it, or note the format gap rather than failing silently.

## Boundaries

- Once the real table region is identified and clean, bulk analysis/reshaping routes to `data-csv` (pandas) — extract the region, then hand off.
- Writing or restyling a workbook is the `xlsx` skill; this reads, it does not author.
- A tidy single-table CSV never needs this — go straight to `data-csv`.
- Charts embedded in the sheet are images — if their content matters, route to `read-image`.
