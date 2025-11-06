import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '@/services/api'


export default function LoginPage() {
const [username, setUsername] = useState('')
const [password, setPassword] = useState('')
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const navigate = useNavigate()


const onSubmit = async (e: React.FormEvent) => {
e.preventDefault()
setLoading(true)
setError(null)
try {
await login(username, password)
navigate('/')
} catch (err: any) {
setError(err.message || 'Login failed')
} finally {
setLoading(false)
}
}


return (
<div className="container max-w-md">
<div className="card">
<h1 className="text-2xl font-semibold mb-4">Login</h1>
<form onSubmit={onSubmit} className="space-y-4">
<div>
<label className="label">Username</label>
<input className="input" value={username} onChange={e=>setUsername(e.target.value)} />
</div>
<div>
<label className="label">Password</label>
<input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
</div>
{error && <p className="text-red-600 text-sm">{error}</p>}
<button className="btn btn-primary w-full" disabled={loading}>
{loading ? 'Signing in…' : 'Sign in'}
</button>
</form>
</div>
</div>
)
}