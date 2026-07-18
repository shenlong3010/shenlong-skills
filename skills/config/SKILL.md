---
name: config
description: Read and write JSON, YAML, and TOML config safely — safe_load only, the YAML Norway problem, datetime serialization, TOML read/write split. Use for "parse this config", "generate YAML", "read pyproject.toml", or any settings-file handling in scripts.
derivation: original
flow: util
---

# config

## YAML

```python
import yaml
cfg = yaml.safe_load(open("cfg.yml"))       # ALWAYS safe_load
```

- **`yaml.load` without a safe loader executes arbitrary Python from the file** — it is a code-execution vector, not a parser choice.
- **Norway problem:** PyYAML is YAML 1.1 — bare `no`, `yes`, `on`, `off` parse as booleans, so `country: no` becomes `False`. Quote such values when writing; when reading foreign YAML, expect it.
- Writing: `yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)`. PyYAML drops comments on round-trip — if comments must survive (editing someone's config), use `ruamel.yaml` instead.

## JSON

```python
import json
json.dump(obj, f, indent=2, default=str)    # default=str: datetimes/Paths/Decimals
data = json.load(f)
```

- `datetime` is not JSON-serializable — `default=str` (lossy) or isoformat explicitly.
- Keys are always strings after round-trip: `{1: "a"}` comes back `{"1": "a"}`.
- Trailing commas and comments are invalid JSON — for human-edited files with comments, that's YAML/TOML territory.

## TOML

```python
import tomllib                              # stdlib 3.11+, READ-ONLY
cfg = tomllib.load(open("pyproject.toml", "rb"))   # binary mode required
```

Writing TOML needs `tomli-w` (stdlib has no writer). Datetimes are first-class in TOML — no default=str dance.

## Choosing
Machine-to-machine → JSON. Human-edited + comments → YAML (quote the Norway words) or TOML. Python packaging → TOML by definition.
