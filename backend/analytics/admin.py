from django.contrib import admin
from .models import Channel, Video


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = (
        "channel_id",
        "title",
        "created_at",
    )
    search_fields = ("channel_id", "title")
    list_filter = ("created_at",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "video_id",
        "title",
        "channel",
        "published_at",
    )
    search_fields = ("video_id", "title", "channel__channel_id")
    list_filter = ("channel", "published_at")
