import re
from urllib.parse import urlparse

from googleapiclient.discovery import build
from django.conf import settings
import requests
from django.conf import settings
from datetime import datetime

def _get_youtube_client():
    """
    Lazily create a YouTube API client.

    We don't want to crash Django at import time if the key is missing.
    Instead, we raise a clear error when someone actually calls resolve_channel_id.
    """
    api_key = getattr(settings, "YOUTUBE_API_KEY", "") or ""
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set. Please set it in your environment or .env file.")
    return build("youtube", "v3", developerKey=api_key)

def resolve_channel_id(raw: str) -> str:
    """
    Accepts:
      - UC_xxx channel ID
      - https://www.youtube.com/channel/UC_xxx
      - https://www.youtube.com/c/CustomName
      - https://www.youtube.com/user/LegacyUser
      - https://www.youtube.com/@handle

    Returns UC_… channel_id or raises ValueError.
    """
    raw = raw.strip()

    # Already a UC_… channel ID?
    if re.fullmatch(r"UC[A-Za-z0-9_-]{20,}", raw):
        return raw

    youtube = _get_youtube_client()

    parts = urlparse(raw)
    path_parts = parts.path.lstrip("/").split("/")

    # Handle pure /@handle case
    if len(path_parts) == 1 and path_parts[0].startswith("@"):
        handle = path_parts[0].lstrip("@")
        resp = (
            youtube.search()
            .list(
                part="snippet",
                q=handle,
                type="channel",
                maxResults=1,
            )
            .execute()
            .get("items", [])
        )
        if resp:
            return resp[0]["snippet"]["channelId"]
        raise ValueError(f"Could not resolve channel handle: {raw}")

    # Handle /channel/UC_xxx , /c/CustomName , /user/LegacyUser , /something/@handle
    if len(path_parts) >= 2:
        kind = path_parts[0].lower()
        ident = path_parts[1]

        # /channel/UC_xxx
        if kind == "channel":
            return ident

        # /c/CustomName or /user/LegacyUser -> resolve by username
        if kind in ("c", "user"):
            resp = (
                youtube.channels()
                .list(part="id", forUsername=ident)
                .execute()
                .get("items", [])
            )
            if resp:
                return resp[0]["id"]

        # /something/@handle (rare, but just in case)
        if ident.startswith("@"):
            handle = ident.lstrip("@")
            resp = (
                youtube.search()
                .list(
                    part="snippet",
                    q=handle,
                    type="channel",
                    maxResults=1,
                )
                .execute()
                .get("items", [])
            )
            if resp:
                return resp[0]["snippet"]["channelId"]

    # If nothing matched above
    raise ValueError(f"Could not resolve channel ID from input: {raw}")


def fetch_videos_for_channel(channel_id: str, max_results: int = 25):
    """
    Fetch recent videos for a channel using the uploads playlist and return
    a list of dicts with all fields needed to populate the Video model.

    Returns a list of:
    {
        "video_id": str,
        "title": str,
        "description": str,
        "published_at": datetime,
        "duration": str,          # ISO 8601, e.g. 'PT10M5S'
        "views": int,
        "likes": int,
        "comments": int,
        "tags": list[str],
    }
    """
    youtube = _get_youtube_client()

    # 1) Get uploads playlist ID for the channel
    ch_resp = (
        youtube.channels()
        .list(part="contentDetails", id=channel_id)
        .execute()
    )
    items = ch_resp.get("items", [])
    if not items:
        raise ValueError(f"No channel found for ID {channel_id}")

    uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # 2) Collect recent video IDs from the uploads playlist
    video_ids: list[str] = []
    page_token = None

    while len(video_ids) < max_results:
        pl_resp = (
            youtube.playlistItems()
            .list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(video_ids)),
                pageToken=page_token or "",
            )
            .execute()
        )

        for item in pl_resp.get("items", []):
            vid = item["contentDetails"]["videoId"]
            video_ids.append(vid)

        page_token = pl_resp.get("nextPageToken")
        if not page_token:
            break

    if not video_ids:
        return []

    # 3) Fetch full details in chunks
    results: list[dict] = []

    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        vids_resp = (
            youtube.videos()
            .list(
                part="snippet,contentDetails,statistics",
                id=",".join(chunk),
                maxResults=len(chunk),
            )
            .execute()
        )

        for item in vids_resp.get("items", []):
            snippet = item["snippet"]
            stats   = item.get("statistics", {})
            content = item.get("contentDetails", {})

            published_at_str = snippet.get("publishedAt")
            published_dt = None
            if published_at_str:
                # Convert '2024-01-01T12:34:56Z' → timezone-aware datetime
                published_dt = datetime.fromisoformat(
                    published_at_str.replace("Z", "+00:00")
                )

            results.append(
                {
                    "video_id":     item["id"],
                    "title":        snippet.get("title", ""),
                    "description":  snippet.get("description", ""),
                    "published_at": published_dt,
                    "duration":     content.get("duration", ""),
                    "views":        int(stats.get("viewCount", 0)),
                    "likes":        int(stats.get("likeCount", 0)),
                    "comments":     int(stats.get("commentCount", 0)),
                    "tags":         snippet.get("tags", []),
                }
            )

    return results
