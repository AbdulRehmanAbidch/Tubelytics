from django.contrib import admin
from django.urls import path

from analytics.views import (
    resolve_channel_view,
    channel_summary_view,
    channel_videos_view,
    fetch_channel_videos_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/channels/resolve/", resolve_channel_view, name="resolve-channel"),
    path(
        "api/channels/<str:channel_id>/summary/",
        channel_summary_view,
        name="channel-summary",
    ),
    path(
        "api/channels/<str:channel_id>/videos/",
        channel_videos_view,
        name="channel-videos",
    ),
    path(
        "api/channels/videos/",
        fetch_channel_videos_view,
        name="fetch-channel-videos",
    ),
]
