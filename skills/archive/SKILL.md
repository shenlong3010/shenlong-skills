---
name: archive
description: Create and extract zip/tar archives safely — zip-slip protection, compression settings, permission semantics. Use for "zip these files", "extract this archive", "bundle the outputs", or any packaging step in a script.
derivation: original
flow: util
domain: system
---

# archive

Stdlib — `zipfile`, `tarfile`, `shutil`.

## Create

```python
import zipfile, shutil
from pathlib import Path

with zipfile.ZipFile("out.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
    for p in Path("build").rglob("*"):
        if p.is_file():
            z.write(p, arcname=p.relative_to("build"))   # arcname or you embed abs paths

shutil.make_archive("out", "gztar", root_dir="build")     # one-liner alternative
```

- **`ZIP_DEFLATED` explicitly** — the default is STORED (no compression at all).
- `arcname=` controls the path inside the archive; forgetting it leaks your directory layout (`/home/user/...`) into the zip.

## Extract — untrusted input is an attack surface

```python
import tarfile
with tarfile.open("in.tgz") as t:
    t.extractall("dest", filter="data")     # 3.12+: blocks path traversal, abs paths, devices
```

- **Zip-slip:** archive members named `../../etc/cron.d/x` escape the target dir on naive extract. `tarfile` `filter="data"` (3.12+) handles tar; for zips, validate every member:

```python
dest = Path("dest").resolve()
for m in z.namelist():
    if not (dest / m).resolve().is_relative_to(dest):
        raise ValueError(f"blocked traversal: {m}")
z.extractall(dest)
```

## Gotchas
- **Zip drops unix permissions** by default — an extracted script isn't executable; restore via each `ZipInfo.external_attr >> 16` or re-`chmod` (this repo's own install docs exist because of this).
- Tar preserves permissions/symlinks — which is exactly why untrusted tars are dangerous.
- Zip has no single-root convention — zips that "explode" 40 files into cwd annoy everyone; put content under one top-level dir.
- Non-UTF-8 member names from legacy Windows zips arrive mojibake (cp437 decode) — `m.encode("cp437").decode("gbk"/"cp932")` recovers common cases.
