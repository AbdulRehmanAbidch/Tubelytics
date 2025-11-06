#!/usr/bin/env python3
"""
streaming.consumer.youtube_consumer
Nauman Shafique — Kafka Consumer & DB integration

Reads youtube.channel_stats and youtube.video_stats, then upserts Django models.
"""

import os
import json
import signal
import sys
from typing import Optional
from kafka import KafkaConsumer

# --- Django setup ---
DJANGO_SETTINGS = os.getenv("DJANGO_SETTINGS_MODULE", "backend.tubelytics.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
import django  # type: ignore
django.setup()

from analytics.ingest import upsert_channel_from_event, upsert_video_from_event  # noqa


CHANNEL_TOPIC = os.getenv("KAFKA_CHANNEL_TOPIC", "youtube.channel_stats")
VIDEO_TOPIC   = os.getenv("KAFKA_VIDEO_TOPIC", "youtube.video_stats")
BOOTSTRAP     = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
GROUP_ID      = os.getenv("KAFKA_GROUP_ID", "tubelytics-consumer")

RUNNING = True

def handle_sig(signum, frame):
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGINT, handle_sig)
signal.signal(signal.SIGTERM, handle_sig)


def main() -> int:
    topics = [CHANNEL_TOPIC, VIDEO_TOPIC]
    print(f"[consumer] connecting to {BOOTSTRAP}, group={GROUP_ID}, topics={topics}")

    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=BOOTSTRAP.split(","),
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        key_deserializer=lambda b: b.decode("utf-8") if b else None,
        consumer_timeout_ms=1000,
    )

    try:
        while RUNNING:
            for msg in consumer.poll(timeout_ms=500, max_records=100).values():
                for record in msg:
                    event = record.value
                    etype = event.get("event_type")
                    try:
                        if etype == "youtube.channel_stats":
                            upsert_channel_from_event(event)
                            print(f"[channel_stats] upserted channel_id={event.get('channel_id')}")
                        elif etype == "youtube.video_stats":
                            upsert_video_from_event(event)
                            print(f"[video_stats] upserted video_id={event.get('video_id')}")
                        else:
                            print(f"[warn] unknown event_type={etype}")
                    except Exception as exc:
                        print(f"[error] failed to process record at offset {record.offset}: {exc}")

    finally:
        consumer.close()
        print("[consumer] shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
