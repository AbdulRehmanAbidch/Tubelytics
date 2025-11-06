# Nauman Shafique — Kafka Consumer & DB Integration

This pack contains everything for **your** side of the project: consumer, DB upserts, indexes, tests, and run docs.

## What you own

- Message contract: `schemas/youtube_events.json`
- Consumer service: `streaming/consumer/youtube_consumer.py`
- ORM upsert helpers: `backend/analytics/ingest.py`
- Admin + verification: `backend/analytics/admin.py` and `python manage.py list_channels`
- DB tuning: `backend/analytics/migrations/0002_add_indexes.py`
- Tests: `backend/analytics/tests/test_ingest_and_summary.py`
- Local Kafka stack: `kafka/docker-compose.kafka.yml`

## How it fits with the team

- Mani’s **producer** sends two event types (`youtube.channel_stats`, `youtube.video_stats`) using the same JSON schema documented here.
- Your **consumer** is idempotent and writes clean rows with indexes for query speed.
- Vamsi’s **frontend** calls the read APIs; your `compute_channel_summary()` returns exactly what those views need.

## Run order

1. `docker compose -f kafka/docker-compose.kafka.yml up -d`
2. Create topics (see `streaming/README.md`).
3. Run Django `migrate` and then apply the indexes migration.
4. Start the consumer: `python streaming/consumer/youtube_consumer.py`.
5. Start Mani’s producer and watch rows appear in Admin.

## Notes

- This replaces the *ETL-focused* ingestion with **Kafka streaming**, but the star-schema/analytics goals from the proposal remain intact.
- Indexes: `channel_id`, `video_id`, `published_at`, and FK `channel`.
- If producer sends `video_stats` first, we create a Channel stub and later enrich it when `channel_stats` arrives.
