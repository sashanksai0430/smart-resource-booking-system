import { useEffect, useState, useCallback } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

const STATUS_COLOR = {
  PENDING: '#f5c451',
  APPROVED: '#4ade80',
  REJECTED: '#f87171',
  CANCELLED: '#9aa1ab',
  COMPLETED: '#60c7f5',
  OVERDUE: '#fb923c',
}

export default function CalendarView() {
  const { user } = useAuth()
  const [resources, setResources] = useState([])
  const [resourceId, setResourceId] = useState('')
  const [events, setEvents] = useState([])
  const [modal, setModal] = useState(null) // { start, end }
  const [purpose, setPurpose] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/resources/').then(({ data }) => {
      setResources(data)
      if (data.length) setResourceId(String(data[0].id))
    })
  }, [])

  const loadEvents = useCallback(async (info) => {
    if (!resourceId) return
    const { data } = await api.get('/bookings/', {
      params: {
        resource_id: resourceId,
        start: info.startStr,
        end: info.endStr,
      },
    })
    setEvents(
      data
        .filter((b) => !['CANCELLED', 'REJECTED'].includes(b.status))
        .map((b) => ({
          id: String(b.id),
          title: `${b.status}${b.user_id === user?.id ? ' (you)' : ''}`,
          start: b.start_time,
          end: b.end_time,
          backgroundColor: STATUS_COLOR[b.status],
          borderColor: STATUS_COLOR[b.status],
        }))
    )
  }, [resourceId, user])

  const handleSelect = (selectInfo) => {
    setError('')
    setPurpose('')
    setModal({ start: selectInfo.startStr, end: selectInfo.endStr })
  }

  const submitBooking = async () => {
    setError('')
    try {
      await api.post('/bookings/', {
        resource_id: Number(resourceId),
        start_time: modal.start,
        end_time: modal.end,
        purpose,
      })
      setModal(null)
      // trigger reload by nudging resourceId dependency via calendar refetch
      const cal = document.querySelector('.fc')
      if (cal) loadEvents({ startStr: modal.start, endStr: modal.end })
    } catch (err) {
      setError(err.response?.data?.detail || 'Booking failed')
    }
  }

  return (
    <div>
      <div className="topbar">
        <h2>Availability Calendar</h2>
        <div style={{ width: 260 }}>
          <select value={resourceId} onChange={(e) => setResourceId(e.target.value)}>
            {resources.map((r) => (
              <option key={r.id} value={r.id}>{r.name} ({r.type})</option>
            ))}
          </select>
        </div>
      </div>

      <FullCalendar
        key={resourceId}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay' }}
        selectable={true}
        selectMirror={true}
        events={events}
        datesSet={loadEvents}
        select={handleSelect}
        height="auto"
        slotMinTime="06:00:00"
        slotMaxTime="22:00:00"
      />

      {modal && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3>New booking request</h3>
          <p style={{ fontSize: 13, color: '#9aa1ab' }}>
            {new Date(modal.start).toLocaleString()} → {new Date(modal.end).toLocaleString()}
          </p>
          <div className="form-row">
            <label>Purpose</label>
            <input value={purpose} onChange={(e) => setPurpose(e.target.value)} placeholder="e.g. Team demo prep" />
          </div>
          {error && <div className="error-text">{error}</div>}
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={submitBooking}>Request Booking</button>
            <button className="secondary" onClick={() => setModal(null)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  )
}
