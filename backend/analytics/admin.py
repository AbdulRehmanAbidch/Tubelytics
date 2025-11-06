from django.contrib import admin
from .models import Channel, Video

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("channel_id", "title", "subscribers", "views_total", "videos_count", "last_snapshot_ts")
    search_fields = ("channel_id", "title", "custom_url", "country")
    list_filter = ("country",)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("video_id", "channel", "title", "views", "likes", "comments", "published_at")
    search_fields = ("video_id", "title", "channel__channel_id", "channel__title")
    list_filter = ("published_at",)
