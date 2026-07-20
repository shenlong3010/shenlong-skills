# Runbook: publish a toolbox change so the live registry serves it

**Trigger:** a skill/command/agent you just merged doesn't appear in a session — `/ralph` missing, new skill absent from the Skill list, retired artifact still showing. Root cause is always the refresh chain: GitHub main → marketplace clone → cache snapshot → session registry (snapshots at session start).

## Preconditions

- Change merged to `main` on GitHub (`git log origin/main --oneline -1` shows it) — the marketplace clone pulls from GitHub, never from your working tree.
- `claude` CLI on PATH.

## Steps

1. **Bump the plugin version** — without this, step 3 no-ops forever.
   ```
   # edit .claude-plugin/plugin.json: "version": "<next-semver>"
   git add .claude-plugin/plugin.json && git commit -m "chore(plugin): bump <next-semver>" && git push origin main
   ```
   **Verify:** `git log origin/main --oneline -1` shows the bump commit.

2. **Refresh the marketplace clone.**
   ```
   claude plugin marketplace update shenlong-skills
   ```
   **Verify:** output says `✔ Successfully updated marketplace`; `git -C ~/.claude/plugins/marketplaces/shenlong-skills log --oneline -1` matches origin/main.

3. **Update the installed plugin (builds a new cache snapshot).**
   ```
   claude plugin update shenlong-skills@shenlong-skills
   ```
   **Verify:** output says `updated from <old> to <new>`. If it says "already at the latest version", the version was not bumped — return to step 1, or force with:
   ```
   claude plugin uninstall shenlong-skills@shenlong-skills && claude plugin install shenlong-skills@shenlong-skills
   ```
   **Verify (either path):** `ls ~/.claude/plugins/cache/shenlong-skills/shenlong-skills/` lists the new version directory containing your changed file.

4. **Restart Claude Code** — the running session's registry snapshot never updates in place.
   **Verify:** in the new session, the changed artifact appears (new agent types are announced at session start; a new skill is invocable via the Skill tool).

## Rollback

Cache keeps prior version directories (`0.1.0/`, `0.2.0/`, …). To pin back: `claude plugin uninstall` then reinstall after resetting the marketplace clone to the older tag/commit — or revert the commit on main and repeat steps 1–4 (preferred; keeps the chain consistent).

## Escalation

Steps 2–3 succeed but the new version directory still lacks your change → the marketplace clone's remote is wrong; check `git -C ~/.claude/plugins/marketplaces/shenlong-skills remote -v` points at the GitHub repo, not a stale fork. Registry still wrong after a confirmed-fresh snapshot + restart → Claude Code bug; file with `claude /bug`.
