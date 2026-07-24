import { useEffect, useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

const TYPES = ['EQUIPMENT', 'ROOM', 'VEHICLE']

export default function Resources() {
  const { user } = useAuth()
  const canManage = user && ['ADMIN', 'MANAGER'].includes(user.role)
  const [resources, setResources] = useState([])
  const [form, setForm] = useState({ name: '', type: 'EQUIPMENT', description: '', location: '', requires_approval: true })
  const [error, setError] = useState('')

  const load = () => api.get('/resources/').then(({ data }) => setResources(data))
  useEffect(() => { load() }, [])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value })
  }

  const create = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/resources/', form)
      setForm({ name: '', type: 'EQUIPMENT', description: '', location: '', requires_approval: true })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create resource')
    }
  }

  const setStatus = async (id, status) => {
    await api.patch(`/resources/${id}`, { status })
    load()
  }

  return (
    <div>
      <div className="topbar"><h2>Resources</h2></div>

      {canManage && (
        <div className="card">
          <h3>Add resource</h3>
          <form onSubmit={create}>
            <div className="grid-2">
              <div className="form-row">
                <label>Name</label>
                <input name="name" value={form.name} onChange={handleChange} required />
              </div>
              <div className="form-row">
                <label>Type</label>
                <select name="type" value={form.type} onChange={handleChange}>
                  {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-row">
                <label>Location</label>
                <input name="location" value={form.location} onChange={handleChange} />
              </div>
              <div className="form-row">
                <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <input type="checkbox" name="requires_approval" style={{ width: 'auto' }}
                    checked={form.requires_approval} onChange={handleChange} />
                  Requires approval
                </label>
              </div>
            </div>
            <div className="form-row">
              <label>Description</label>
              <textarea name="description" value={form.description} onChange={handleChange} rows={2} />
            </div>
            {error && <div className="error-text">{error}</div>}
            <button type="submit">Add Resource</button>
          </form>
        </div>
      )}

      <div className="card">
        <table>
          <thead>
            <tr><th>Name</th><th>Type</th><th>Location</th><th>Status</th><th>Approval</th>{canManage && <th></th>}</tr>
          </thead>
          <tbody>
            {resources.map((r) => (
              <tr key={r.id}>
                <td>{r.name}</td>
                <td>{r.type}</td>
                <td>{r.location || '—'}</td>
                <td>{r.status}</td>
                <td>{r.requires_approval ? 'Required' : 'Auto'}</td>
                {canManage && (
                  <td>
                    {r.status === 'ACTIVE'
                      ? <button className="secondary" onClick={() => setStatus(r.id, 'MAINTENANCE')}>Set Maintenance</button>
                      : <button onClick={() => setStatus(r.id, 'ACTIVE')}>Reactivate</button>}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
