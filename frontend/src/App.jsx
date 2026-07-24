import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import CalendarView from './pages/CalendarView'
import MyBookings from './pages/MyBookings'
import Resources from './pages/Resources'
import Approvals from './pages/Approvals'
import Penalties from './pages/Penalties'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<CalendarView />} />
            <Route path="/my-bookings" element={<MyBookings />} />
            <Route path="/resources" element={<Resources />} />
            <Route
              path="/approvals"
              element={
                <ProtectedRoute roles={['ADMIN', 'MANAGER']}>
                  <Approvals />
                </ProtectedRoute>
              }
            />
            <Route path="/penalties" element={<Penalties />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
