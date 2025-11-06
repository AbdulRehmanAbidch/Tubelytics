import re
from urllib.parse import urlparse

from googleapiclient.discovery import build
from django.conf import settings


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

        # /@handle style
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

    raise ValueError(f"Could not resolve channel ID from input: {raw}")
