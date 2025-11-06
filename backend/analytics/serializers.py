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


class ChannelSummarySerializer(serializers.Serializer):
    channel_id            = serializers.CharField()
    title                 = serializers.CharField()
    description           = serializers.CharField(allow_blank=True)
    subscribers           = serializers.IntegerField()
    total_videos          = serializers.IntegerField()
    total_views           = serializers.IntegerField()
    total_video_views     = serializers.IntegerField()
    total_video_likes     = serializers.IntegerField()
    total_video_comments  = serializers.IntegerField()


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
