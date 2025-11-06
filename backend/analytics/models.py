from django.db import models
from django.contrib.auth.models import User


class Channel(models.Model):
    channel_id   = models.CharField(max_length=64, unique=True)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    subscribers  = models.BigIntegerField(default=0)
    total_videos = models.BigIntegerField(default=0)
    total_views  = models.BigIntegerField(default=0)

    requested_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="channels",
    )

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title or self.channel_id


class Video(models.Model):
    video_id     = models.CharField(max_length=64, unique=True)
    channel      = models.ForeignKey(
        Channel,
        related_name="videos",
        on_delete=models.CASCADE,
    )

    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    published_at = models.DateTimeField()
    duration     = models.CharField(max_length=32)  # keep ISO 8601 like "PT10M5S"

    views        = models.BigIntegerField(default=0)
    likes        = models.BigIntegerField(default=0)
    comments     = models.BigIntegerField(default=0)

    tags         = models.JSONField(default=list, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
