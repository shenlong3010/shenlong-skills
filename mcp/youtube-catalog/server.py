#!/usr/bin/env python3
"""youtube-catalog — MCP server over the YouTube Data API v3 (list-only).

Three tools, all 1-quota-unit calls: enumerate a playlist, enumerate a
channel's uploads, and fetch metadata for known video IDs. No search.list —
it costs 100 units/call against a 10,000/day free quota, and the enumeration
tools cover the actual use case (a playlist pasted as a curriculum) without
touching the expensive endpoint at all.

The transcript itself is NOT this server's job — the youtube-transcript MCP
tool already does that. This server exists for the one thing that tool can't
do: turn a playlist or channel URL into the list of video IDs in it, plus
title/description/duration/views per video, so a caller (or talk-notes) can
decide what to fetch transcripts for without opening each video by hand.

Auth: YOUTUBE_API_KEY env var, from Google Cloud Console (enable "YouTube
Data API v3", create an API key, restrict it to that API). Never pass the
key as a literal or put it in .mcp.json.

Run:  python server.py
Wire: see README.md (uvx --with fastmcp, absolute path, ~/.claude.json)
"""
import os
import re
from urllib.parse import urlparse, parse_qs

import requests
from fastmcp import FastMCP

mcp = FastMCP("youtube-catalog")

API_KEY = os.environ["YOUTUBE_API_KEY"]
BASE = "https://www.googleapis.com/youtube/v3"
MAX_RESULTS = 50          # YouTube's own per-page cap for list endpoints
DEFAULT_PAGE = 25         # curated default so one call doesn't dump 50 rows
MAX_IDS_PER_METADATA_CALL = 50


def _get(path: str, params: dict) -> dict:
    params = {**params, "key": API_KEY}
    resp = requests.get(f"{BASE}/{path}", params=params, timeout=15)
    if resp.status_code == 403:
        body = resp.text[:300]
        raise RuntimeError(
            f"YouTube API 403 — quota exhausted or key not authorized for "
            f"YouTube Data API v3. Response: {body}"
        )
    if resp.status_code == 404:
        raise RuntimeError("Not found — check the ID/URL was extracted correctly.")
    resp.raise_for_status()
    return resp.json()


def _extract_playlist_id(url_or_id: str) -> str:
    """Accept a playlist URL, watch URL with &list=, or a bare ID."""
    s = url_or_id.strip()
    if s.startswith("PL") or s.startswith("UU") or s.startswith("LL") or s.startswith("FL"):
        return s
    parsed = urlparse(s)
    qs = parse_qs(parsed.query)
    if "list" in qs:
        return qs["list"][0]
    raise ValueError(
        f"Could not find a playlist ID in '{url_or_id}'. Pass a playlist URL "
        f"(youtube.com/playlist?list=...), a watch URL with &list=..., or the "
        f"bare playlist ID (starts with PL/UU/LL/FL)."
    )


def _extract_channel_ref(url_or_id: str) -> tuple[str, str]:
    """Return (kind, value) where kind is 'id' or 'handle'."""
    s = url_or_id.strip()
    if re.fullmatch(r"UC[\w-]{22}", s):
        return ("id", s)
    if s.startswith("@"):
        return ("handle", s)
    parsed = urlparse(s)
    path = parsed.path.strip("/")
    if path.startswith("channel/"):
        return ("id", path.split("/", 1)[1])
    if path.startswith("@"):
        return ("handle", path)
    if path.startswith("c/") or path.startswith("user/"):
        raise ValueError(
            f"'{url_or_id}' uses a legacy /c/ or /user/ vanity URL, which the "
            f"API can't resolve directly. Open the channel and use its @handle "
            f"or the /channel/UC... URL instead."
        )
    raise ValueError(
        f"Could not find a channel ID or @handle in '{url_or_id}'. Pass a "
        f"channel URL (youtube.com/@handle or youtube.com/channel/UC...), a "
        f"bare @handle, or the bare UC... channel ID."
    )


def _extract_video_id(url_or_id: str) -> str:
    s = url_or_id.strip()
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    parsed = urlparse(s)
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    if parsed.netloc in ("youtu.be",):
        return parsed.path.strip("/")
    raise ValueError(f"Could not find a video ID in '{url_or_id}'.")


def _iso8601_duration_to_hms(d: str) -> str:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return d or "?"
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return f"{h}:{mi:02d}:{s:02d}" if h else f"{mi}:{s:02d}"


@mcp.tool()
def list_playlist_items(playlist: str, page_size: int = DEFAULT_PAGE, page_token: str = "") -> str:
    """List the videos in a YouTube playlist, in playlist order.

    Use when the user pastes a playlist URL (or bare playlist ID) and you need
    the video IDs/titles it contains — e.g. to process each as a talk-notes
    curriculum. Costs 1 quota unit per call regardless of page_size.

    playlist: playlist URL, a watch URL containing &list=, or a bare playlist ID.
    page_size: rows to return, max 50 (YouTube's cap). Default 25.
    page_token: pass the nextPageToken from a prior call to continue; empty for page 1.

    Returns: one line per video (position, videoId, title, channel), the total
    playlist size, and a nextPageToken if more pages remain.
    """
    try:
        pid = _extract_playlist_id(playlist)
    except ValueError as e:
        return f"Error: {e}"

    size = max(1, min(page_size, MAX_RESULTS))
    params = {"part": "snippet", "playlistId": pid, "maxResults": size}
    if page_token:
        params["pageToken"] = page_token

    try:
        data = _get("playlistItems", params)
    except (RuntimeError, requests.HTTPError) as e:
        return f"Error: {e}"

    items = data.get("items", [])
    if not items:
        return f"No items found for playlist '{pid}' — it may be empty, private, or the ID is wrong."

    total = data.get("pageInfo", {}).get("totalResults", "?")
    lines = [f"Playlist {pid} — {total} videos total"]
    for it in items:
        sn = it["snippet"]
        pos = sn.get("position", "?")
        vid = sn.get("resourceId", {}).get("videoId", "?")
        title = sn.get("title", "?")
        channel = sn.get("videoOwnerChannelTitle", sn.get("channelTitle", "?"))
        lines.append(f"{pos}: {vid} — {title} ({channel})")

    cursor = data.get("nextPageToken")
    if cursor:
        lines.append(f"\n[more results — call again with page_token={cursor!r}]")
    return "\n".join(lines)


@mcp.tool()
def list_channel_videos(channel: str, page_size: int = DEFAULT_PAGE, page_token: str = "") -> str:
    """List a channel's uploaded videos, newest first.

    Use when the user pastes a channel URL (@handle or /channel/UC...) and you
    need its videos — e.g. to browse what's available before picking talks to
    process. Costs 1 quota unit for the channel lookup (first call only, cached
    per-process) + 1 unit per page.

    channel: channel URL (youtube.com/@handle or /channel/UC...), a bare @handle,
        or a bare UC... channel ID.
    page_size: rows to return, max 50. Default 25.
    page_token: pass the nextPageToken from a prior call to continue; empty for page 1.

    Returns: one line per video (videoId, title, published date), and a
    nextPageToken if more pages remain.
    """
    try:
        kind, value = _extract_channel_ref(channel)
    except ValueError as e:
        return f"Error: {e}"

    try:
        if kind == "handle":
            ch = _get("channels", {"part": "contentDetails,snippet", "forHandle": value})
        else:
            ch = _get("channels", {"part": "contentDetails,snippet", "id": value})
    except (RuntimeError, requests.HTTPError) as e:
        return f"Error: {e}"

    ch_items = ch.get("items", [])
    if not ch_items:
        return f"No channel found for '{channel}'."

    channel_title = ch_items[0]["snippet"]["title"]
    uploads_playlist = ch_items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    size = max(1, min(page_size, MAX_RESULTS))
    params = {"part": "snippet", "playlistId": uploads_playlist, "maxResults": size}
    if page_token:
        params["pageToken"] = page_token

    try:
        data = _get("playlistItems", params)
    except (RuntimeError, requests.HTTPError) as e:
        return f"Error: {e}"

    items = data.get("items", [])
    if not items:
        return f"No videos found for channel '{channel_title}'."

    total = data.get("pageInfo", {}).get("totalResults", "?")
    lines = [f"Channel: {channel_title} — {total} videos total"]
    for it in items:
        sn = it["snippet"]
        vid = sn.get("resourceId", {}).get("videoId", "?")
        title = sn.get("title", "?")
        published = (sn.get("publishedAt") or "?")[:10]
        lines.append(f"{vid} — {title} ({published})")

    cursor = data.get("nextPageToken")
    if cursor:
        lines.append(f"\n[more results — call again with page_token={cursor!r}]")
    return "\n".join(lines)


@mcp.tool()
def get_video_metadata(video_ids: str) -> str:
    """Get title, channel, duration, view count, and publish date for one or more videos.

    Use for triage before deciding what to watch/process — batch several video
    IDs at once instead of opening each video page. Costs 1 quota unit per call
    regardless of how many IDs are batched (up to 50).

    video_ids: comma-separated video URLs and/or bare 11-char video IDs (max 50).

    Returns: one block per video with title, channel, duration, views, and
    publish date; unresolved IDs are listed separately.
    """
    raw_ids = [s for s in (x.strip() for x in video_ids.split(",")) if s]
    if not raw_ids:
        return "Error: no video IDs provided."
    if len(raw_ids) > MAX_IDS_PER_METADATA_CALL:
        return f"Error: {len(raw_ids)} IDs given, max {MAX_IDS_PER_METADATA_CALL} per call."

    try:
        ids = [_extract_video_id(r) for r in raw_ids]
    except ValueError as e:
        return f"Error: {e}"

    try:
        data = _get("videos", {"part": "snippet,contentDetails,statistics", "id": ",".join(ids)})
    except (RuntimeError, requests.HTTPError) as e:
        return f"Error: {e}"

    items = data.get("items", [])
    found_ids = {it["id"] for it in items}
    missing = [i for i in ids if i not in found_ids]

    blocks = []
    for it in items:
        sn, cd, st = it["snippet"], it["contentDetails"], it.get("statistics", {})
        blocks.append(
            f"{it['id']}: {sn.get('title', '?')}\n"
            f"  channel: {sn.get('channelTitle', '?')}\n"
            f"  duration: {_iso8601_duration_to_hms(cd.get('duration', ''))}\n"
            f"  views: {st.get('viewCount', '?')}\n"
            f"  published: {(sn.get('publishedAt') or '?')[:10]}\n"
            f"  description: {(sn.get('description') or '').splitlines()[0][:200] if sn.get('description') else '(none)'}"
        )

    out = "\n\n".join(blocks) if blocks else "No videos resolved."
    if missing:
        out += f"\n\nUnresolved IDs: {', '.join(missing)}"
    return out


if __name__ == "__main__":
    mcp.run()
