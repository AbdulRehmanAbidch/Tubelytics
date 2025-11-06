import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from 'recharts'


type Props = {
data: Array<{ title: string; views: number; likes: number; comments: number }>
sortKey: 'views' | 'likes' | 'comments'
}


export default function TopVideosBar({ data, sortKey }: Props) {
return (
<div className="h-80 w-full">
<ResponsiveContainer>
<BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 60 }}>
<CartesianGrid strokeDasharray="3 3" />
<XAxis dataKey="title" interval={0} angle={-25} textAnchor="end" height={80} tick={{ fontSize: 12 }} />
<YAxis />
<Tooltip formatter={(value: any) => (Number(value)).toLocaleString()} />
<Bar dataKey={sortKey} />
</BarChart>
</ResponsiveContainer>
</div>
)
}