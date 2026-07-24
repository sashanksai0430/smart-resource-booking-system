# Smart Resource & Equipment Booking System

Multi-role (Admin / Manager / User) booking platform for shared assets — equipment, rooms, vehicles — with an interactive calendar, approval workflows, overlap prevention, and automated fines for late returns.

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT auth, APScheduler
- **Frontend:** React (Vite), FullCalendar, React Router, Axios

## Features
- **RBAC:** ADMIN / MANAGER / USER roles enforced on every endpoint.
- **Interactive calendar:** click-drag a time slot on the FullCalendar view to request a booking; color-coded by status.
- **Overlap prevention:** bookings for the same resource can never have overlapping PENDING/APPROVED/OVERDUE time ranges (`app/services/overlap.py`).
- **Approval workflow:** USER bookings need MANAGER/ADMIN sign-off (unless a resource is flagged `requires_approval=False`); ADMIN/MANAGER bookings auto-approve.
- **Automated reminders & fines:** a background APScheduler job (every 15 min) flags overdue bookings and creates a `Penalty` once a grace period is exceeded (`app/services/reminders.py`).
- **Usage tracking:** every booking records who approved it, when, and when the asset was actually returned.

## Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then edit DATABASE_URL / SECRET_KEY
```
Create the Postgres database referenced in `.env` (or point `DATABASE_URL` at `sqlite:///./dev.db` for quick local testing — no Postgres install needed).

```bash
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

The first registered user is a normal USER. Promote someone to ADMIN directly in the DB the first time:
```sql
UPDATE users SET role = 'ADMIN' WHERE username = 'your_username';
```
After that, admins can promote others via `PATCH /users/{id}/role`.

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Runs at http://localhost:5173 and expects the API at http://localhost:8000 (override with a `VITE_API_URL` env var / `.env` file if needed).

## Project structure
```
backend/
  app/
    main.py          # app factory, CORS, scheduler lifespan
    models.py         # User, Resource, Booking, Penalty
    schemas.py         # Pydantic request/response models
    auth.py             # JWT + password hashing + role guards
    routers/
      auth.py, users.py, resources.py, bookings.py, penalties.py
    services/
      overlap.py       # slot overlap check
      reminders.py      # APScheduler job: overdue detection + fines
frontend/
  src/
    api/client.js       # axios instance + auth interceptor
    context/AuthContext.jsx
    components/          # Layout, ProtectedRoute
    pages/
      Login, Register, CalendarView, MyBookings, Resources, Approvals, Penalties
```

## Notes / next steps
- Reminders currently log to the console — swap in an email/SMS provider inside `reminders.py` for production use.
- Add Alembic migrations before deploying (the app currently just calls `create_all` on startup).
- Deploy backend to Railway/Render, frontend to Vercel, matching your Ledger/Smart Library projects.
