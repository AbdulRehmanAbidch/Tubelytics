"""
analytics.ingest
Helpers that Nauman's Kafka consumer will call to upsert Channel/Video rows.
These are safe to import in tests and in the consumer.
"""
from __future__ import annotations
from typing import Dict, Any
from django.utils import timezone
from django.db import transaction
from .models import Channel, Video


def _get(event: Dict[str, Any], *keys, default=None):
    cur = event
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


@transaction.atomic
def upsert_channel_from_event(event: Dict[str, Any]) -> Channel:
    """
    Expects an event matching schemas/youtube_events.json -> youtube.channel_stats
    Required: channel_id
    """
    channel_id = event.get("channel_id")
    if not channel_id:
        raise ValueError("channel_id missing in channel_stats event")

    stats = event.get("statistics", {}) or {}
    snapshot_ts = event.get("snapshot_ts") or event.get("emitted_at")

    defaults = dict(
        title=event.get("title") or "",
        custom_url=event.get("custom_url"),
        country=event.get("country"),
        description=event.get("description") or "",
        subscribers=stats.get("subscribers"),
        views_total=stats.get("views"),
        videos_count=stats.get("videos"),
        last_snapshot_ts=snapshot_ts or timezone.now(),
    )
    obj, _created = Channel.objects.update_or_create(
        channel_id=channel_id,
        defaults=defaults,
    )
    return obj


@transaction.atomic
def upsert_video_from_event(event: Dict[str, Any]) -> Video:
    """
    Expects an event matching schemas/youtube_events.json -> youtube.video_stats
    Required: video_id, channel_id
    """
    video_id = event.get("video_id")
    channel_id = event.get("channel_id")
    if not video_id or not channel_id:
        raise ValueError("video_id or channel_id missing in video_stats event")

    stats = event.get("statistics", {}) or {}
    snapshot_ts = event.get("snapshot_ts") or event.get("emitted_at")

    # Make sure Channel exists (create a minimal stub if producer sent video first)
    channel, _ = Channel.objects.get_or_create(channel_id=channel_id, defaults={"title": ""})

    defaults = dict(
        channel=channel,
        title=event.get("title") or "",
        published_at=event.get("published_at"),
        duration_seconds=event.get("duration_seconds"),
        views=stats.get("views"),
        likes=stats.get("likes"),
        comments=stats.get("comments"),
        last_snapshot_ts=snapshot_ts or timezone.now(),
    )
    obj, _created = Video.objects.update_or_create(
        video_id=video_id,
        defaults=defaults,
    )
    return obj


def compute_channel_summary(channel_id: str, limit: int = 10, order_by: str = "views") -> dict:
    """
    Aggregates a summary suitable for GET /api/channels/{channel_id}/summary/.
    Returns a dict that a serializer can turn into JSON.
    """
    from django.db.models import Sum

    chan = Channel.objects.get(channel_id=channel_id)
    qs = Video.objects.filter(channel=chan)
    agg = qs.aggregate(
        total_views=Sum("views"),
        total_likes=Sum("likes"),
        total_comments=Sum("comments"),
    )
    if order_by not in {"views", "likes", "comments"}:
        order_by = "views"

    top_videos = list(
        qs.order_by(f"-{order_by}")
        .values("video_id", "title", "views", "likes", "comments", "published_at")
        [: limit]
    )

    return {
        "channel_id": channel_id,
        "title": chan.title,
        "subscribers": chan.subscribers,
        "views_total": chan.views_total,
        "videos_count": chan.videos_count,
        "last_snapshot_ts": chan.last_snapshot_ts,
        "aggregates": {
            "total_views": agg["total_views"] or 0,
            "total_likes": agg["total_likes"] or 0,
            "total_comments": agg["total_comments"] or 0,
        },
        "top_videos": top_videos,
        "ordered_by": order_by,
        "limit": limit,
    }
