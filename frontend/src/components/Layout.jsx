import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const canManage = user && ['ADMIN', 'MANAGER'].includes(user.role)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>📦 Booking System</h2>
        <nav>
          <NavLink to="/" end>Calendar</NavLink>
          <NavLink to="/my-bookings">My Bookings</NavLink>
          <NavLink to="/resources">Resources</NavLink>
          {canManage && <NavLink to="/approvals">Approvals</NavLink>}
          <NavLink to="/penalties">Fines</NavLink>
        </nav>
        <div style={{ marginTop: 40, fontSize: 13, color: '#9aa1ab' }}>
          <div>{user?.username}</div>
          <div className={`badge ${user?.role === 'ADMIN' ? 'APPROVED' : user?.role === 'MANAGER' ? 'PENDING' : 'COMPLETED'}`} style={{ marginTop: 6, display: 'inline-block' }}>
            {user?.role}
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
          </div>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
