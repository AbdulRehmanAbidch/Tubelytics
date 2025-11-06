from django.db import models
from django.contrib.auth.models import User


class Channel(models.Model):
    channel_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.channel_id


class Video(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="videos")
    video_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    view_count = models.BigIntegerField(default=0)
    like_count = models.BigIntegerField(default=0)
    comment_count = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title