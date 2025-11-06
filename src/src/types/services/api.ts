const BASE = import.meta.env.VITE_API_BASE_URL || '/api'


async function http<T>(path: string, options?: RequestInit): Promise<T> {
const res = await fetch(`${BASE}${path}`, {
headers: { 'Content-Type': 'application/json' },
credentials: 'include',
...options,
})
if (!res.ok) {
const text = await res.text()
throw new Error(text || `HTTP ${res.status}`)
}
return res.json() as Promise<T>
}


export function login(username: string, password: string) {
// Placeholder – wire up to your chosen auth endpoint
return http<{ detail: string }>(`/auth/login/`, {
method: 'POST',
body: JSON.stringify({ username, password })
})
}


export function resolveChannel(raw: string) {
return http<{ channel_id: string; title?: string }>(`/channels/resolve/`, {
method: 'POST',
body: JSON.stringify({ raw })
})
}


export function getChannelSummary(channelId: string) {
return http(`/channels/${channelId}/summary/`)
}


export function getChannelVideos(channelId: string) {
return http(`/channels/${channelId}/videos/`)
}