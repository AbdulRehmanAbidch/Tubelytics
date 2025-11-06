from rest_framework import serializers
from .models import Channel, Video


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            "channel_id",
            "title",
            "description",
            "subscribers",
            "total_videos",
            "total_views",
        ]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            "video_id",
            "title",
            "description",
            "published_at",
            "duration",
            "views",
            "likes",
            "comments",
            "tags",
        ]
