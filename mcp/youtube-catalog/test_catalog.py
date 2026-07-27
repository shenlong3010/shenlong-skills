#!/usr/bin/env python3
"""Smoke: URL/ID extraction (no key needed) + live API calls (needs YOUTUBE_API_KEY).

Run: python test_catalog.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Extraction helpers don't need a key, but importing server.py does (module-level
# os.environ["YOUTUBE_API_KEY"]) — set a dummy if unset, real tests skip anyway.
os.environ.setdefault("YOUTUBE_API_KEY", "test-dummy-key")
import server as S  # noqa: E402


def check(label: str, got, want) -> None:
    status = "ok" if got == want else "FAIL"
    print(f"[{status}] {label}: got={got!r} want={want!r}")
    if got != want:
        FAILURES.append(label)


FAILURES: list[str] = []


def test_extraction() -> None:
    check("playlist bare id", S._extract_playlist_id("PLxyz123"), "PLxyz123")
    check("playlist url", S._extract_playlist_id(
        "https://www.youtube.com/playlist?list=PLabc"), "PLabc")
    check("playlist from watch url", S._extract_playlist_id(
        "https://www.youtube.com/watch?v=abc123&list=PLdef"), "PLdef")

    check("channel bare id", S._extract_channel_ref("UC" + "x" * 22),
          ("id", "UC" + "x" * 22))
    check("channel bare handle", S._extract_channel_ref("@someone"),
          ("handle", "@someone"))
    check("channel url handle", S._extract_channel_ref(
        "https://www.youtube.com/@someone"), ("handle", "@someone"))
    check("channel url id", S._extract_channel_ref(
        "https://www.youtube.com/channel/UC" + "y" * 22),
        ("id", "UC" + "y" * 22))
    try:
        S._extract_channel_ref("https://www.youtube.com/c/legacyname")
        check("legacy /c/ raises", False, True)
    except ValueError:
        check("legacy /c/ raises", True, True)

    check("video bare id", S._extract_video_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")
    check("video watch url", S._extract_video_id(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")
    check("video short url", S._extract_video_id(
        "https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    check("duration hms", S._iso8601_duration_to_hms("PT1H2M3S"), "1:02:03")
    check("duration ms only", S._iso8601_duration_to_hms("PT4M5S"), "4:05")


def test_live() -> None:
    if os.environ.get("YOUTUBE_API_KEY", "test-dummy-key") == "test-dummy-key":
        print("[skip] live API tests — set a real YOUTUBE_API_KEY to run them")
        return

    # A small, stable public playlist (YouTube's own "First YouTube video" upload).
    out = S.get_video_metadata("dQw4w9WgXcQ")
    check("live metadata contains title marker", "views:" in out, True)


def main() -> None:
    test_extraction()
    test_live()
    if FAILURES:
        sys.exit(f"{len(FAILURES)} failure(s): {FAILURES}")
    print("all checks passed")


if __name__ == "__main__":
    main()
