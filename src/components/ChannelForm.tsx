import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { resolveChannel } from '@/services/api'


export default function ChannelForm() {
const [raw, setRaw] = useState('')
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const navigate = useNavigate()


const onSubmit = async (e: React.FormEvent) => {
e.preventDefault()
setLoading(true)
setError(null)
try {
const res = await resolveChannel(raw)
navigate(`/channels/${res.channel_id}`)
} catch (err: any) {
setError(err.message || 'Could not resolve channel')
} finally {
setLoading(false)
}
}


return (
<form onSubmit={onSubmit} className="space-y-3">
<label className="label">YouTube Channel URL or ID</label>
<input
className="input"
placeholder="https://www.youtube.com/@SomeCreator or UCxxxxxxxx"
value={raw}
onChange={(e) => setRaw(e.target.value)}
/>
{error && <p className="text-red-600 text-sm">{error}</p>}
<button className="btn btn-primary" disabled={loading}>
{loading ? 'Resolving…' : 'Resolve & View Report'}
</button>
</form>
)
}