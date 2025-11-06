import { Link, NavLink } from 'react-router-dom'


export default function Navbar() {
return (
<nav className="nav">
<div className="container flex items-center justify-between py-3">
<Link to="/" className="text-xl font-semibold">Tubelytics</Link>
<div className="flex items-center gap-4 text-sm">
<NavLink to="/" className={({isActive}) => isActive ? 'font-semibold' : ''}>Dashboard</NavLink>
<NavLink to="/login" className={({isActive}) => isActive ? 'font-semibold' : ''}>Login</NavLink>
</div>
</div>
</nav>
)
}