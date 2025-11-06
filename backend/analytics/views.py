from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # you can switch to IsAuthenticated later
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from .models import Channel, Video
from .serializers import (
    ChannelSerializer,
    ChannelSummarySerializer,
    VideoSerializer,
)
from .utils import resolve_channel_id, fetch_videos_for_channel


@api_view(["POST"])
@permission_classes([AllowAny])
def resolve_channel_view(request):
    """
    POST /api/channels/resolve/
    Body: { "channel": "<url or id>" }

    Resolves a YouTube channel URL or ID into a canonical UC_… channel_id.
    Creates a Channel row if it doesn't exist yet (with empty stats).
    """
    raw = request.data.get("channel")
    if not raw:
        return Response(
            {"detail": "Field 'channel' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        channel_id = resolve_channel_id(raw)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    channel, created = Channel.objects.get_or_create(
        channel_id=channel_id,
        defaults={
            "title": "",
            "description": "",
            "subscribers": 0,
            "total_videos": 0,
            "total_views": 0,
        },
    )

    data = {
        "channel_id": channel.channel_id,
        "created": created,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def channel_summary_view(request, channel_id: str):
    """
    GET /api/channels/<channel_id>/summary/

    Returns basic channel info + aggregated stats from videos.
    """
    try:
        channel = Channel.objects.get(channel_id=channel_id)
    except Channel.DoesNotExist:
        return Response({"detail": "Channel not found."}, status=status.HTTP_404_NOT_FOUND)

    agg = Video.objects.filter(channel=channel).aggregate(
        total_video_views=Sum("views"),
        total_video_likes=Sum("likes"),
        total_video_comments=Sum("comments"),
    )

    payload = {
        "channel_id":           channel.channel_id,
        "title":                channel.title,
        "description":          channel.description,
        "subscribers":          channel.subscribers,
        "total_videos":         channel.total_videos,
        "total_views":          channel.total_views,
        "total_video_views":    agg["total_video_views"] or 0,
        "total_video_likes":    agg["total_video_likes"] or 0,
        "total_video_comments": agg["total_video_comments"] or 0,
    }

    serializer = ChannelSummarySerializer(payload)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def channel_videos_view(request, channel_id: str):
    """
    GET /api/channels/<channel_id>/videos/?sort=-views&limit=50

    Returns a list of videos for this channel, with simple sorting and limiting:
      - sort: any field on Video model (e.g. views, -views, likes, -likes, published_at)
      - limit: max number of videos to return (int)
    """
    try:
        channel = Channel.objects.get(channel_id=channel_id)
    except Channel.DoesNotExist:
        return Response({"detail": "Channel not found."}, status=status.HTTP_404_NOT_FOUND)

    sort = request.query_params.get("sort", "-views")
    try:
        limit = int(request.query_params.get("limit", 50))
    except ValueError:
        limit = 50

    qs = Video.objects.filter(channel=channel).order_by(sort)[:limit]
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def fetch_channel_videos_view(request):
    """
    POST /api/channels/videos/
    Body: { "channel_id": "<UC_xxx>" }

    Convenience endpoint to fetch latest videos from YouTube for a channel_id
    and store/update them in the Video table.
    """
    channel_id = request.data.get("channel_id")
    if not channel_id:
        return Response(
            {"detail": "Field 'channel_id' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        channel = Channel.objects.get(channel_id=channel_id)
    except Channel.DoesNotExist:
        return Response(
            {"detail": "Channel not found. Resolve it first via /api/channels/resolve/."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        videos_data = fetch_videos_for_channel(channel_id)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    for v in videos_data:
        Video.objects.update_or_create(
            video_id=v["video_id"],
            defaults={
                "channel":      channel,
                "title":        v["title"],
                "description":  v.get("description", ""),
                "published_at": v["published_at"],
                "duration":     v.get("duration", ""),
                "views":        v.get("views", 0),
                "likes":        v.get("likes", 0),
                "comments":     v.get("comments", 0),
                "tags":         v.get("tags", []),
            },
        )

    qs = Video.objects.filter(channel=channel).order_by("-published_at")
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
