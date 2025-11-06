import ChannelForm from '@/components/ChannelForm'


export default function DashboardPage() {
return (
<div className="space-y-6">
<h1 className="text-2xl font-semibold">Dashboard</h1>
<div className="card">
<ChannelForm />
</div>
</div>
)
}