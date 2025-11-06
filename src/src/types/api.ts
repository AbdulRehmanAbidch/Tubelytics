export type ResolveChannelResponse = {
channel_id: string
title?: string
};


export type ChannelSummary = {
channel_id: string
title: string
subscribers: number
total_views: number
total_videos: number
last_snapshot_ts?: string
};


export type Video = {
video_id: string
title: string
views: number
likes: number
comments: number
published_at: string
};