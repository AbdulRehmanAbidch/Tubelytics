import { Line, LineChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from 'recharts'


type Item = { title: string; views: number; published_at: string }


function toSeries(items: Item[]) {
return items
.filter(i => i?.published_at)
.map(i => ({ ...i, date: new Date(i.published_at) }))
.sort((a, b) => a.date.getTime() - b.date.getTime())
.map(i => ({ date: i.date.toISOString().slice(0,10), views: Number(i.views) || 0 }))
}


export default function ViewsOverTimeLine({ data }: { data: Item[] }) {
const series = toSeries(data)
return (
<div className="h-80 w-full">
<ResponsiveContainer>
<LineChart data={series} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
<CartesianGrid strokeDasharray="3 3" />
<XAxis dataKey="date" />
<YAxis />
<Tooltip formatter={(value: any) => (Number(value)).toLocaleString()} />
<Line type="monotone" dataKey="views" dot={false} />
</LineChart>
</ResponsiveContainer>
</div>
)
}