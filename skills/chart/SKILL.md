---
name: chart
description: Render charts headlessly with matplotlib for reports, decks, and docs — Agg backend, figure lifecycle, savefig settings, date axes. Use for "plot this", "chart for the report", or generating any PNG/SVG figure that feeds docx, pptx, or a README.
derivation: original
---

# chart

```bash
pip install matplotlib
```

## Headless shape (scripts, CI, servers)

```python
import matplotlib
matplotlib.use("Agg")                # BEFORE importing pyplot; no display needed
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 4.5))     # OO API, not plt.plot state-machine
ax.plot(xs, ys, label="p95 latency")
ax.set_xlabel("day"); ax.set_ylabel("ms"); ax.legend()
fig.autofmt_xdate()                          # readable date ticks
fig.savefig("chart.png", dpi=150, bbox_inches="tight")
plt.close(fig)                               # REQUIRED in loops — figures leak memory
```

## Gotchas
- **`plt.close(fig)` in any loop** — matplotlib keeps every figure alive; a 500-chart batch without close eats gigabytes and warns at 20 figures.
- `bbox_inches="tight"` or labels get clipped; `dpi=150` for docs, 200+ for print.
- Prefer the OO API (`fig, ax`) over `plt.*` state calls — the state machine breaks the moment two charts are built in one scope.
- Dates: plot real datetimes, not strings; strings plot in occurrence order and lie.
- Transparent background for slide compositing: `fig.savefig(..., transparent=True)`.

## Handoff
Feeds directly into the other skills: `docx` `add_picture("chart.png", width=Inches(5.5))`, `pptx` `add_picture(..., Inches(7))`. Render at the final display width's aspect ratio to avoid downstream distortion.
