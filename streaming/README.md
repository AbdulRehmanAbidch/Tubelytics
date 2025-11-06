# Streaming Consumer (Nauman Shafique)

This folder contains the Kafka **consumer** that reads producer events and writes them into the Django DB.

## Topics (contract)

- `youtube.channel_stats` — one message per channel snapshot.
- `youtube.video_stats` — one message per video snapshot.

The JSON schemas are described in `../schemas/youtube_events.json`.

## Prereqs

- Python 3.10+
- Django app available (project module: `backend.tubelytics` and app: `analytics`)
- Packages: `pip install kafka-python django python-dotenv` (dotenv optional)
- Running Kafka (see `../kafka/docker-compose.kafka.yml`)

## Quick start

1) Start Kafka locally (Docker):

```bash
cd kafka
docker compose -f docker-compose.kafka.yml up -d
# Create topics
docker exec kafka kafka-topics --create --topic youtube.channel_stats --bootstrap-server localhost:9094 --partitions 1 --replication-factor 1
docker exec kafka kafka-topics --create --topic youtube.video_stats   --bootstrap-server localhost:9094 --partitions 1 --replication-factor 1
```

2) Configure environment (copy `.env.sample` to `.env` or export variables):

```bash
export DJANGO_SETTINGS_MODULE=backend.tubelytics.settings
export KAFKA_BOOTSTRAP_SERVERS=localhost:9094
export KAFKA_GROUP_ID=tubelytics-consumer
```

3) Run the consumer from repo root:

```bash
python streaming/consumer/youtube_consumer.py
```

You should see logs like:

```
[channel_stats] upserted channel_id=UC123...
[video_stats] upserted video_id=Vxyz...
```

4) Verify data:

```bash
python manage.py list_channels
```

## DB expectations

- `analytics.Channel` and `analytics.Video` exist with fields referenced in `analytics/ingest.py`.
- Index migration provided at `backend/analytics/migrations/0002_add_indexes.py`.

## Notes

- The consumer is idempotent via `update_or_create`.
- If a `video_stats` arrives before the channel, a minimal `Channel` stub is created (with blank title). The next `channel_stats` will fill the details.
