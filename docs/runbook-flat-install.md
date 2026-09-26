# Runbook — flat install (marketplace-blocked machine)

For a machine that cannot install the plugin. `docs/runbook-plugin-refresh.md`
covers the plugin path; this covers the one the work machine actually uses.

## What the flat path delivers

`tools/sync-flat.sh` copies **skills, commands, agents, and hook handlers**, and
generates hook wiring. It does not copy `styles/`, `templates/`, `mcp/`,
`tools/`, or `evals/` — clone the repo if those are wanted.

## Procedure

```bash
git clone <repo> && cd shenlong-skills

# 1. Dry run FIRST. Writes nothing. Reports [new] / [EXISTS, managed] /
#    [EXISTS, NOT managed] per target so a pending clobber is visible.
bash tools/sync-flat.sh --prefix shenlong- --include-extra

# 2. Apply once the report looks right.
bash tools/sync-flat.sh --prefix shenlong- --include-extra --apply
```

**`--prefix shenlong-`** — a flat `~/.claude/skills/` has no namespace, so bare
names collide with native and Anthropic skills. The prefix rewrites the dir name
and the frontmatter `name:` on the **copy only**; canonical repo names stay
unprefixed. Vendored (`derivation: copied`) skills keep upstream identity unless
`--prefix-vendored` is passed.

**`--include-extra`** — omit it and `/ralph` breaks: the command ships in core
but `ralph-plan`/`ralph-next` live in `extra/skills/`. Omit deliberately if the
38 extra skills aren't wanted and `/ralph` isn't either.

## Wiring the hooks

Skills load from disk; **hooks do not**. `hooks/hooks.json` uses
`${CLAUDE_PLUGIN_ROOT}`, which only exists for an installed plugin, so the sync
writes `$DEST/hooks-settings.json` with resolved absolute paths instead.

Merge it into `~/.claude/settings.json` by hand, under the top-level `hooks`
key. It is a side file on purpose — a generated merge into a file holding your
own hooks is where unrelated config gets dropped.

```bash
cat ~/.claude/hooks-settings.json     # inspect before merging
```

**Windows:** the handlers are POSIX bash. Without Git Bash on PATH they are
*wired-but-dead* — present in settings, silently never firing. The generator
detects Git Bash and emits the launcher prefix; if it warns that Git Bash is
missing, install it or port the handlers before trusting any guard.

## Verify — do not skip

Files landing proves nothing about wiring. Take a command string verbatim out of
the generated JSON and run it:

```bash
seq 1 500 > /tmp/big.txt
printf '{"tool_input":{"file_path":"/tmp/big.txt"}}' \
  | bash ~/.claude/hooks/guard-bulk-read.sh; echo "rc=$? (expect 2)"
```

`rc=2` with a block message means the handler works. Then confirm the escape:
the same payload with `"offset":1,"limit":50` must exit 0. If the guard blocks
but no escape works, stop — a block with an unreachable escape is worse than no
guard.

Then, in a real session, confirm `/skills` lists the prefixed skills.

## Re-syncing

Re-run the same command. Dirs created by a previous sync carry a
`.sync-flat-managed` marker and are replaced; anything without one is **skipped
with a warning**, so hand-authored or hand-edited skills survive. If a skill was
deliberately edited in place, expect it to be skipped from then on — edit it in
the repo instead.

Pruning is not automatic: skills deleted or renamed upstream, and copies left
under a previously-used prefix, persist until removed by hand.
