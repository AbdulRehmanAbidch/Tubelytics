import { useEffect, useMemo, useState } from 'react'


export default function ChannelReportPage() {
const { channelId } = useParams()
const [summary, setSummary] = useState<any>(null)
const [videos, setVideos] = useState<any[]>([])
const [limit, setLimit] = useState(10)
const [sortKey, setSortKey] = useState<'views'|'likes'|'comments'>('views')
const [error, setError] = useState<string | null>(null)


useEffect(() => {
if (!channelId) return
Promise.all([
getChannelSummary(channelId),
getChannelVideos(channelId)
]).then(([s, v]) => {
setSummary(s)
setVideos(v)
}).catch(err => setError(err.message || 'Failed to load channel'))
}, [channelId])


const topVideos = useMemo(() => {
const sorted = [...videos].sort((a, b) => b[sortKey] - a[sortKey])
return sorted.slice(0, limit)
}, [videos, limit, sortKey])


if (error) return <p className="text-red-600">{error}</p>
if (!summary) return <p>Loading…</p>


return (
<div className="space-y-6">
<header className="flex flex-wrap items-end justify-between gap-4">
<div>
<h1 className="text-2xl font-semibold">{summary.title}</h1>
<p className="text-sm text-gray-600">Channel ID: {summary.channel_id}</p>
</div>
<div className="flex gap-2">
<div className="card text-center">
<p className="text-sm text-gray-600">Subscribers</p>
<p className="text-xl font-semibold">{summary.subscribers.toLocaleString()}</p>
</div>
<div className="card text-center">
<p className="text-sm text-gray-600">Total Views</p>
<p className="text-xl font-semibold">{summary.total_views.toLocaleString()}</p>
</div>
<div className="card text-center">
<p className="text-sm text-gray-600">Total Videos</p>
<p className="text-xl font-semibold">{summary.total_videos.toLocaleString()}</p>
</div>
</div>
</header>


<section className="card space-y-4">
<div className="flex items-center gap-3">
<label className="label !mb-0">Top N</label>
<select className="input max-w-[120px]" value={limit} onChange={e=>setLimit(parseInt(e.target.value))}>
{[10,20,50].map(n => <option key={n} value={n}>{n}</option>)}
</select>
<label className="label !mb-0">Sort by</label>
<select className="input max-w-[160px]" value={sortKey} onChange={e=>setSortKey(e.target.value as any)}>
<option value="views">Views</option>
<option value="likes">Likes</option>
<option value="comments">Comments</option>
</select>
</div>
<TopVideosBar data={topVideos} sortKey={sortKey} />
</section>


<section className="card">
<ViewsOverTimeLine data={videos} />
</section>
</div>
)
}