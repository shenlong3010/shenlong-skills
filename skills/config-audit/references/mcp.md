# Auditing MCP servers

## Inventory — check every MCP source
MCP servers can be configured in more than one place; enumerate all before judging:
- `~/.claude.json` — the primary user-scope server set (the CLI's main store).
- `.mcp.json` (project root, and `~/.mcp.json`) — project/user `mcpServers`, opted
  in per project via `enabledMcpjsonServers` in `settings.json` / `settings.local.json`.
- Servers are NOT configured in `settings.json`'s own body — but `settings.json`
  is what *enables* the `.mcp.json` ones, so read both.

Then compare the configured set against what actually connected this session
(`claude mcp list`, `claude mcp get <name>`, or a SessionStart audit log if one
exists). Changes require a **restart** to reload.

## Dead / stale servers (cleanup)
- A server configured but timing out, auth-rejected (401), or pointing at a
  removed local scaffold is pure startup cost — every session pays the connection
  attempt (often a multi-second timeout) for nothing.
- A server whose backing code was deleted from the repo but left in `~/.claude.json`
  still tries to connect. Cross-check configured servers against what still exists.
- Distinguish causes: `CONNECT_TIMEOUT` (server down / wrong command),
  `AUTH_HEADER_REJECTED` / 401 (bad or expired token — when an explicit
  `Authorization` header is set, OAuth fallback is disabled), missing binary. A
  connection failure is not the same as "capability doesn't exist" — say which.

## Token / cache cost (the big one)
MCP schemas sit high in the cache prefix (system prompt → tools → **MCP schemas**
→ skills → memory → conversation). Consequences:
- Every enabled server's tool schemas load into every session as standing tokens —
  a large or unused server is a permanent tax. Disable servers you don't use this
  session.
- **Toggling MCP mid-session breaks the cache** from that point down — decide the
  server set before the first prompt. MCP churn is one of the largest avoidable
  cache-break costs. Propose enable/disable changes as "next session start".

## Disable vs remove
- No CLI `disable` verb exists (only `add`/`remove`/`logout`). To keep a config for
  later (e.g. a token that'll be fixed) without connecting, toggle it off per-project
  via interactive `/mcp` rather than `remove`.
- Deleting a plugin's cache dir is NOT uninstalling — a marketplace entry in
  `known_marketplaces.json` / `installed_plugins.json` can re-clone on update. Full
  removal is `claude plugin marketplace remove` (user action).

## Enhancement
- A capability being done by hand each session that a pre-vetted MCP server would
  automate → propose adding it (decide server set before session start).
- A server returning huge responses uncached → route through response caching
  (`caching` skill) or narrow its tool set.

## Verify
`claude mcp get <name>` for one server's real status; restart and re-list after any
change (config is read at startup only).
