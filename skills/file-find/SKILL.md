---
name: file-find
description: Find files fast by name, age, or size — fd for scoped search, plocate for instant system-wide indexed lookup, and the find fallback. Use for "where is that file", "newest/biggest files", "files changed since X", or any filename hunt — use INSTEAD of `find` spelunking or `ls -R`; content search belongs to code-search, not here.
derivation: original
flow: lookup
domain: system
---

# File Find

## fd — the scoped default

```bash
fd 'Publisher'                       # name pattern, gitignore-aware, fast
fd -e java -t f 'Handler'            # extension + files-only
fd --changed-within 1d               # what changed today (post-incident favorite)
fd -S +50M -t f                      # big files
fd -H -E node_modules 'config'       # -H include hidden, -E exclude
fd -e log -X rm                      # batch-exec on all results (-x = per-result)
```

Same filtering philosophy as rg: respects `.gitignore`, skips hidden — `-I`/`-u` are the escape hatches when the target is deliberately ignored.

## plocate — the indexed lane

```bash
plocate SnsPublisher.java            # instant, system-wide — reads an index, not the disk
sudo updatedb                        # refresh the index (usually a daily cron)
```

The zoekt-of-filenames: milliseconds regardless of tree size. Trade-off is staleness — files created since the last `updatedb` are invisible; a miss means "not indexed", not "not present". Verify absence with `fd` before concluding.

**Windows: plocate does not exist.** The indexed lane there is Everything (voidtools, `es` CLI) if installed; otherwise stay on `fd` (`-u` when the target may be ignored/hidden) — it is fast enough that the index rarely pays for itself on a single repo.

## find — the portable fallback

```bash
find . -name '*.yml' -mtime -2 -size +1M     # everywhere fd isn't installed (containers, remote boxes)
```

Slower and noisier, but POSIX-ubiquitous; know the three flags above and skip the rest.

## Size archaeology

```bash
du -xah . | sort -rh | head -20      # biggest things under here, one filesystem
```

## Boundaries

- Content inside files → `code-search`; deleted-but-open files eating disk → `system-lookup` (`lsof +L1`); archives' contents → `archive` skill's listing patterns (`unzip -l`, `tar -tf`).
