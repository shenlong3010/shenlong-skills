---
name: mcp-builder
description: Conventions for building a FastMCP server that is safe and pleasant for agents to use. Consult whenever writing or reviewing an MCP server — "new MCP server", "wrap this API for the agent", "review my MCP tools".
derivation: adapted
source: https://github.com/anthropics/skills
---

# MCP Builder

## Skeleton
```python
from fastmcp import FastMCP
import os

mcp = FastMCP("service-name")
API_KEY = os.environ["SERVICE_API_KEY"]   # env var — never a literal, never in .mcp.json

@mcp.tool()
def search_items(query: str, limit: int = 10) -> str:
    """One sentence of what it does. When to use it. What it returns."""
    ...
```

## Conventions
- **Credentials:** environment variables only. A key committed in config is the incident.
- **Tool descriptions are the agent's UI:** one line what, one line when, one line return shape. Vague descriptions cause wrong-tool calls; bloated ones cost every session's context.
- **Return curated text, not raw dumps:** page, truncate, and summarize server-side; note total counts. The agent's context is the scarce resource.
- **Annotations honest:** mark tools readOnly vs destructive vs idempotent; a destructive tool mislabeled readOnly defeats every downstream permission gate.
- **Scope minimal:** expose the 5 operations the agent needs, not the API's 40. Each extra tool costs description tokens and misuse surface.
- **Errors as actionable text:** return what failed and what a valid call looks like — the agent retries from your message.
