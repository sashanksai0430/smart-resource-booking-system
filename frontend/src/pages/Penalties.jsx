import { useEffect, useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Penalties() {
  const { user } = useAuth()
  const canManage = user && ['ADMIN', 'MANAGER'].includes(user.role)
  const [penalties, setPenalties] = useState([])

  const load = () => api.get('/penalties/').then(({ data }) => setPenalties(data))
  useEffect(() => { load() }, [])

  const markPaid = async (id) => {
    await api.patch(`/penalties/${id}/pay`)
    load()
  }

  const total = penalties.filter((p) => !p.is_paid).reduce((s, p) => s + p.amount, 0)

  return (
    <div>
      <div className="topbar">
        <h2>Fines & Penalties</h2>
        <div style={{ fontSize: 14, color: '#f5c451' }}>Outstanding: ₹{total.toFixed(2)}</div>
      </div>
      <div className="card">
        <table>
          <thead>
            <tr><th>Booking</th><th>Reason</th><th>Amount</th><th>Status</th>{canManage && <th></th>}</tr>
          </thead>
          <tbody>
            {penalties.map((p) => (
              <tr key={p.id}>
                <td>#{p.booking_id}</td>
                <td>{p.reason}</td>
                <td>₹{p.amount.toFixed(2)}</td>
                <td><span className={`badge ${p.is_paid ? 'COMPLETED' : 'PENDING'}`}>{p.is_paid ? 'PAID' : 'UNPAID'}</span></td>
                {canManage && (
                  <td>{!p.is_paid && <button onClick={() => markPaid(p.id)}>Mark Paid</button>}</td>
                )}
              </tr>
            ))}
            {penalties.length === 0 && (
              <tr><td colSpan={5} style={{ color: '#9aa1ab' }}>No penalties on record.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
