from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # or IsAuthenticated later
from rest_framework.response import Response
from rest_framework import status

from .models import Channel
from .serializers import ChannelSerializer
from .utils import resolve_channel_id


@api_view(["POST"])
@permission_classes([AllowAny])  # change to IsAuthenticated later if you want
def resolve_channel_view(request):
    """
    Accepts JSON body: { "channel": "<url or id>" }
    - Resolves the UC_… channel_id using YouTube API
    - Creates Channel row if it doesn't exist yet (only channel_id for now)
    - Returns { channel_id, created }
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
            # we'll fill these later when consumer/producer runs
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
