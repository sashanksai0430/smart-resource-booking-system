import { useEffect, useState } from 'react'
import api from '../api/client'

export default function MyBookings() {
  const [bookings, setBookings] = useState([])
  const [resourcesById, setResourcesById] = useState({})

  const load = async () => {
    const [{ data: b }, { data: r }] = await Promise.all([
      api.get('/bookings/', { params: { mine_only: true } }),
      api.get('/resources/'),
    ])
    setBookings(b)
    setResourcesById(Object.fromEntries(r.map((x) => [x.id, x.name])))
  }

  useEffect(() => { load() }, [])

  const cancel = async (id) => {
    await api.post(`/bookings/${id}/cancel`)
    load()
  }

  return (
    <div>
      <div className="topbar"><h2>My Bookings</h2></div>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Resource</th><th>Start</th><th>End</th><th>Purpose</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((b) => (
              <tr key={b.id}>
                <td>{resourcesById[b.resource_id] || b.resource_id}</td>
                <td>{new Date(b.start_time).toLocaleString()}</td>
                <td>{new Date(b.end_time).toLocaleString()}</td>
                <td>{b.purpose || '—'}</td>
                <td><span className={`badge ${b.status}`}>{b.status}</span></td>
                <td>
                  {['PENDING', 'APPROVED'].includes(b.status) && (
                    <button className="danger" onClick={() => cancel(b.id)}>Cancel</button>
                  )}
                </td>
              </tr>
            ))}
            {bookings.length === 0 && (
              <tr><td colSpan={6} style={{ color: '#9aa1ab' }}>No bookings yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
