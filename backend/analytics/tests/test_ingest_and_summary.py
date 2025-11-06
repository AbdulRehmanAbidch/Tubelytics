from django.test import TestCase
from django.utils import timezone
from analytics.models import Channel, Video
from analytics.ingest import upsert_channel_from_event, upsert_video_from_event, compute_channel_summary

class IngestTests(TestCase):
    def test_channel_upsert(self):
        evt = {
            "event_type": "youtube.channel_stats",
            "emitted_at": "2025-11-05T00:00:00Z",
            "channel_id": "UC123",
            "title": "Sample Channel",
            "statistics": {"subscribers": 10, "views": 111, "videos": 2},
        }
        ch = upsert_channel_from_event(evt)
        self.assertEqual(ch.channel_id, "UC123")
        self.assertEqual(ch.subscribers, 10)
        self.assertEqual(ch.views_total, 111)
        self.assertEqual(ch.videos_count, 2)

    def test_video_upsert_and_summary(self):
        upsert_channel_from_event({
            "event_type": "youtube.channel_stats",
            "emitted_at": "2025-11-05T00:00:00Z",
            "channel_id": "UC123",
            "title": "Sample Channel",
        })
        v1 = upsert_video_from_event({
            "event_type": "youtube.video_stats",
            "emitted_at": "2025-11-05T00:01:00Z",
            "video_id": "V1",
            "channel_id": "UC123",
            "title": "First",
            "published_at": "2024-01-01T00:00:00Z",
            "duration_seconds": 120,
            "statistics": {"views": 100, "likes": 5, "comments": 1}
        })
        v2 = upsert_video_from_event({
            "event_type": "youtube.video_stats",
            "emitted_at": "2025-11-05T00:02:00Z",
            "video_id": "V2",
            "channel_id": "UC123",
            "title": "Second",
            "published_at": "2024-01-02T00:00:00Z",
            "duration_seconds": 60,
            "statistics": {"views": 50, "likes": 10, "comments": 0}
        })
        self.assertEqual(Video.objects.count(), 2)
        summary = compute_channel_summary("UC123", limit=1, order_by="views")
        self.assertEqual(summary["aggregates"]["total_views"], 150)
        self.assertEqual(len(summary["top_videos"]), 1)
        self.assertEqual(summary["top_videos"][0]["video_id"], "V1")
