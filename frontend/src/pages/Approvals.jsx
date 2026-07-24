import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Approvals() {
  const [pending, setPending] = useState([])
  const [resourcesById, setResourcesById] = useState({})

  const load = async () => {
    const [{ data: p }, { data: r }] = await Promise.all([
      api.get('/bookings/pending-approvals'),
      api.get('/resources/'),
    ])
    setPending(p)
    setResourcesById(Object.fromEntries(r.map((x) => [x.id, x.name])))
  }

  useEffect(() => { load() }, [])

  const decide = async (id, approve) => {
    try {
      await api.post(`/bookings/${id}/decision`, { approve })
      load()
    } catch (err) {
      alert(err.response?.data?.detail || 'Action failed')
    }
  }

  return (
    <div>
      <div className="topbar"><h2>Pending Approvals</h2></div>
      <div className="card">
        <table>
          <thead>
            <tr><th>Resource</th><th>Start</th><th>End</th><th>Purpose</th><th></th></tr>
          </thead>
          <tbody>
            {pending.map((b) => (
              <tr key={b.id}>
                <td>{resourcesById[b.resource_id] || b.resource_id}</td>
                <td>{new Date(b.start_time).toLocaleString()}</td>
                <td>{new Date(b.end_time).toLocaleString()}</td>
                <td>{b.purpose || '—'}</td>
                <td style={{ display: 'flex', gap: 8 }}>
                  <button onClick={() => decide(b.id, true)}>Approve</button>
                  <button className="danger" onClick={() => decide(b.id, false)}>Reject</button>
                </td>
              </tr>
            ))}
            {pending.length === 0 && (
              <tr><td colSpan={5} style={{ color: '#9aa1ab' }}>Nothing pending.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
