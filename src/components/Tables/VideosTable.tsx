import { useMemo, useState } from 'react'
}


type Props = { rows: Row[] }


export default function VideosTable({ rows }: Props) {
const [q, setQ] = useState('')
const [sortKey, setSortKey] = useState<'views'|'likes'|'comments'|'published_at'>('views')
const [dir, setDir] = useState<'asc'|'desc'>('desc')


const data = useMemo(() => {
const filtered = q
? rows.filter(r => r.title?.toLowerCase().includes(q.toLowerCase()))
: rows
const sorted = [...filtered].sort((a, b) => {
const av = sortKey === 'published_at' ? new Date(a.published_at).getTime() : Number(a[sortKey]) || 0
const bv = sortKey === 'published_at' ? new Date(b.published_at).getTime() : Number(b[sortKey]) || 0
return dir === 'asc' ? av - bv : bv - av
})
return sorted
}, [rows, q, sortKey, dir])


const toggleSort = (key: typeof sortKey) => {
if (sortKey === key) setDir(d => (d === 'asc' ? 'desc' : 'asc'))
else { setSortKey(key); setDir('desc') }
}


return (
<div className="space-y-3">
<div className="flex items-center gap-2">
<input className="input max-w-sm" placeholder="Filter by title…" value={q} onChange={e=>setQ(e.target.value)} />
</div>


<div className="overflow-x-auto">
<table className="min-w-full text-sm">
<thead>
<tr className="text-left border-b">
<th className="py-2 pr-4">Title</th>
<th className="py-2 pr-4 cursor-pointer" onClick={()=>toggleSort('views')}>Views</th>
<th className="py-2 pr-4 cursor-pointer" onClick={()=>toggleSort('likes')}>Likes</th>
<th className="py-2 pr-4 cursor-pointer" onClick={()=>toggleSort('comments')}>Comments</th>
<th className="py-2 pr-4 cursor-pointer" onClick={()=>toggleSort('published_at')}>Published</th>
</tr>
</thead>
<tbody>
{data.map(r => (
<tr key={r.video_id} className="border-b hover:bg-gray-50">
<td className="py-2 pr-4 max-w-[420px] truncate" title={r.title}>{r.title}</td>
<td className="py-2 pr-4">{Number(r.views||0).toLocaleString()}</td>
<td className="py-2 pr-4">{Number(r.likes||0).toLocaleString()}</td>
<td className="py-2 pr-4">{Number(r.comments||0).toLocaleString()}</td>
<td className="py-2 pr-4">{r.published_at ? new Date(r.published_at).toLocaleDateString() : '-'}</td>
</tr>
))}
</tbody>
</table>
</div>
</div>
)
}