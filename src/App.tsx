import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from '@/components/Layout/Navbar'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import ChannelReportPage from '@/pages/ChannelReportPage'


export default function App() {
return (
<div className="min-h-screen">
<Navbar />
<main className="container py-6">
<Routes>
<Route path="/login" element={<LoginPage />} />
<Route path="/" element={<DashboardPage />} />
<Route path="/channels/:channelId" element={<ChannelReportPage />} />
<Route path="*" element={<Navigate to="/" replace />} />
</Routes>
</main>
</div>
)
}