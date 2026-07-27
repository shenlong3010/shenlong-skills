# youtube-catalog — MCP server over the YouTube Data API v3 (list-only)

Turns a playlist or channel URL into the list of videos it contains, plus
batch metadata (title/duration/views) for known video IDs. It does **not**
fetch transcripts — that's the `youtube-transcript` MCP tool's job. This
server exists for the gap that tool can't fill: enumeration.

## Why no search

`search.list` costs 100 quota units per call against a 10,000/day free quota
— about 100 searches/day, ceiling included. The three tools here (playlist
items, channel uploads, video metadata) each cost **1 unit** per call, so
personal use never realistically hits the daily cap. Search was scoped out
deliberately rather than built and rationed.

## Get an API key

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select a project.
2. APIs & Services → Library → enable **YouTube Data API v3**.
3. APIs & Services → Credentials → Create Credentials → API key.
4. Restrict the key to "YouTube Data API v3" (recommended, not required).
5. No billing account needed for the free 10,000 units/day tier.

## Wire it

```json
{ "mcpServers": { "youtube-catalog": {
    "type": "stdio",
    "command": "uvx",
    "args": ["--with", "fastmcp>=3", "--with", "requests", "python",
             "C:/Users/you/path/to/mcp/youtube-catalog/server.py"],
    "env": { "YOUTUBE_API_KEY": "your-key-here" } } } }
```

Set in `~/.claude.json` (global user scope) — the CLI reads MCP config **only**
from there, never `settings.json`. Restart required before tools appear.

The key goes in the `env` block of the MCP config, not the repo, not a
committed file. `~/.claude.json` lives outside version control by convention;
double-check before committing if you ever touch that file directly.

## Tools

| tool | what it gives you | cost |
|---|---|---|
| `list_playlist_items(playlist, page_size, page_token)` | videos in a playlist, in order | 1 unit/page |
| `list_channel_videos(channel, page_size, page_token)` | a channel's uploads, newest first | 1 unit (channel lookup) + 1 unit/page |
| `get_video_metadata(video_ids)` | title/duration/views/description for up to 50 videos at once | 1 unit/call |

All three accept either a pasted URL or a bare ID — paste whatever you have,
the server extracts the ID. Legacy `/c/` and `/user/` vanity channel URLs
can't be resolved by the API; use the channel's `@handle` or `/channel/UC...`
URL instead (the tool's error message says so).

## Where this fits

Built for the case: a playlist as a self-study curriculum (e.g. "distributed
systems talks I want to watch"). `list_playlist_items` gets the video list;
each video's transcript still goes through `youtube-transcript` +
`talk-notes` individually — token math doesn't change (a 1-hour transcript
is still ~12-16k tokens), so a 10-video playlist is still 10 separate
`talk-notes` passes synthesized from their output notes, not one session
holding all 10 transcripts. This server only replaces the "open each video
by hand to find its ID" step.

## Limits (v1, deliberate)

List-only — no search, no captions/comments, no write access (playlist
mutation, likes, subscriptions). Legacy vanity channel URLs unsupported (API
limitation, not this server's). No caching of its own; wrap it in
`cache-proxy`'s `upstreams.json` if repeated calls against the same playlist
become common enough to matter.

Requirements: `fastmcp>=3`, `requests>=2.31`.
Test: `uvx --with fastmcp --with requests python test_catalog.py` (needs
`YOUTUBE_API_KEY` set — hits the real API against a small fixed playlist).
