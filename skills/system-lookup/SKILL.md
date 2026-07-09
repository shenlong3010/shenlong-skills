---
name: system-lookup
description: Find what's happening on a machine — which process holds a port or file, what a process is running with, where disk space went, which service logs matter. Use for "port already in use", "who has this file open", "what is this process", "disk full but can't find the files", or any runtime who/what/where question — use INSTEAD of `ps aux | grep` guessing.
derivation: original
---

# System Lookup

Runtime truth beats config reading — ask the kernel, not the manifest.

## Ports and sockets

```bash
ss -tlnp | rg 8080            # who listens on 8080 (modern; needs root for process names)
lsof -i :8080                 # the classic; -sTCP:LISTEN to filter
```

## Files and the disk-space mystery

```bash
lsof /var/log/app.log         # who holds this file open
fuser -v /mnt/data            # processes using a mount (why umount fails)
lsof +L1                      # deleted-but-still-open files — the classic "df says full, du disagrees" answer
du -xah / 2>/dev/null | sort -rh | head -20   # where the space actually went (-x: one filesystem)
```

## Processes

```bash
pgrep -af gunicorn                     # find by full command line
readlink /proc/<pid>/exe               # which binary is ACTUALLY running (post-upgrade ghosts)
tr '\0' '\n' < /proc/<pid>/environ     # the env it launched with (null-separated!)
ls -l /proc/<pid>/cwd /proc/<pid>/fd   # working dir + open fds
ps aux --sort=-%mem | head             # memory hogs; --sort=-%cpu for CPU
pstree -p <pid>                        # parentage — who spawned this
```

## Service logs

```bash
journalctl -u app.service --since '1 hour ago' -p warning
```

Dumps beyond a screen → `log-triage` for clustering.

## Gotchas

- `ss`/`lsof` show process names only with privileges — empty name column means rerun with sudo, not "no owner".
- `/proc/<pid>/environ` is the *launch* environment; it does not update if the process mutates env later.
- Unscoped `lsof` (no path/port arg) walks every fd on the box — slow; always scope.

## Boundaries

- Log content analysis → `log-triage`; stack traces → `stacktrace-analyzer`; container-namespace lookups (nsenter, crictl) are environment-specific — probe availability first (rule 9).
