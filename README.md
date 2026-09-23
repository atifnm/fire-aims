# FIRE-AIMS
**Fire Inspection, Recording & Equipment Asset Information Management System**

A production-quality web application for a Fire Department / Fire & Rescue Department to manage, inspect, monitor,
and maintain fire safety equipment: fire extinguishers, hose cabinets, hose reels, branches/nozzles, and Manual
Call Points (MCPs).

This is a real, runnable full-stack application — not a mockup. It has a database, authentication, role-based
access control, CRUD operations, an inspection workflow with configurable checklists, QR/barcode generation and
camera-based scanning, automatic due-date/status calculation, notifications, a dashboard with analytics, and
CSV/Excel/PDF reports.

---

## 1. Architecture

```
fire-aims/
├── backend/          FastAPI + SQLAlchemy + Alembic (Python)
│   ├── app/
│   │   ├── core/          config, database session, security (JWT/bcrypt), auth deps
│   │   ├── models/        SQLAlchemy models (users, assets, inspections, etc.)
│   │   ├── schemas/       Pydantic request/response schemas
│   │   ├── routers/       REST API endpoints, one file per resource
│   │   ├── services/      QR/barcode generation, status engine, notifications
│   │   ├── seed.py        Demo data generator
│   │   └── main.py        App entrypoint
│   ├── alembic/            Database migrations
│   └── tests/               Pytest test suite
├── frontend/          React + Vite + Tailwind (PWA)
│   └── src/
│       ├── pages/          One file per screen (Dashboard, Assets, Scan, etc.)
│       ├── components/     Shared UI (Nav, StatusBadge, modals)
│       ├── context/         Auth context
│       └── api/              Axios client + offline inspection queue
└── docker-compose.yml   Postgres + backend + frontend, wired together
```

**Stack**: React 18 + Vite + Tailwind (frontend) · FastAPI + SQLAlchemy + Alembic (backend) · SQLite (local/dev,
zero config) or PostgreSQL (recommended for production, wired up in docker-compose) · JWT authentication with
bcrypt password hashing · `qrcode` + `python-barcode` for QR/Code128 generation · `html5-qrcode` for
browser-camera scanning · `reportlab`/`pandas`/`openpyxl` for PDF/CSV/Excel reports · APScheduler for a daily
background job that recalculates statuses and generates due-date notifications.

---

## 2. Features implemented

- **Branding**: the app uses the organization's logo (`frontend/public/brand/logo.svg`) and its exact brand
  colors — deep green `#00401A` and gold `#CAA202` — as the Tailwind color palette (`fire-*` / `gold-*` in
  `tailwind.config.js`). The logo has no embedded font (it's outlined vector paths, not text), so the UI
  typeface is **Poppins** (loaded from Google Fonts, cached for offline PWA use), chosen as a close visual
  match to the logo's bold geometric wordmark — swap it in `index.html` / `tailwind.config.js` if you have a
  specific brand typeface in mind.
- **Editing assets and users**: Admins can edit any asset's location, manufacturer/model/serial number,
  installation date, remarks, and type-specific fields (extinguisher type/capacity, hose length, etc.) from
  either the Assets list (inline pencil icon) or the asset detail page. Equipment type itself is locked once
  created, since changing it would mean swapping which detail table the asset uses. Admins can likewise edit
  any user's name, phone, role, active status, and reset their password from the Users page — employee code
  and email stay fixed once an account exists, since email is the login identifier.
- **Deleting assets**: Admins can permanently delete an asset from its detail page. This is a genuinely
  destructive, cascading action — it also deletes the asset's entire inspection, maintenance, and defect
  history, not just the asset record — so the confirmation dialog shows exactly what will be lost and
  requires typing the asset's ID to proceed, the same "type to confirm" pattern GitHub uses for deleting a
  repo. Deletion is audit-logged. If equipment is only temporarily out of service, prefer editing its status
  over deleting the record, to keep its compliance history intact.
- **Authentication & roles**: JWT login, bcrypt-hashed passwords, Admin / Supervisor / Inspector roles enforced
  on every endpoint that needs it.
- **Locations**: Building → Floor → Room/Area hierarchy, with filtering.
- **All 5 equipment types** as first-class assets (extinguisher, hose cabinet, hose reel, branch/nozzle, MCP),
  each with a shared core record plus type-specific detail fields. Hose cabinet components (reel/branch/MCP)
  link to their parent cabinet via `parent_asset_id`.
- **Auto-generated Asset IDs** (`FE-00001`, `HC-00001`, ...) plus a QR code and a Code128 barcode per asset,
  generated the moment it's created, downloadable/printable from the asset page.
- **Configurable inspection checklists** per equipment type (Admin can add/edit/remove checklist items and
  sections), matching the default checklists in the spec (fire extinguisher, hose cabinet incl. hose reel /
  branch / water supply / MCP sub-sections, standalone hose reel, standalone branch, standalone MCP).
- **Mobile scan → inspect workflow**: camera-based QR/barcode scanning (`html5-qrcode`) with a manual code-entry
  fallback, asset summary, dynamic checklist rendering, Pass/Fail/N/A per item, overall result, remarks, defect
  + corrective action + risk priority capture, photo upload, submit.
- **Automatic status engine**: 🟢 Compliant / 🟡 Due Soon / 🟠 Due Today / 🔴 Overdue / ⚠️ Defective /
  🔧 Under Maintenance / ❌ Out of Service, recalculated on every inspection, maintenance record, and defect
  change, plus once a day via a background job. Thresholds and per-type inspection intervals are configurable
  in Settings, not hard-coded.
- **Maintenance/refill records**: append-only history, never overwritten.
- **Defects & corrective action**: auto-created when an inspection fails or needs maintenance, with severity
  (low/medium/high/critical), assignment, due date, and status tracking (open → assigned → in progress →
  resolved → verified).
- **Inspection review workflow**: Supervisors approve or return inspections; approved inspections are locked.
- **Admin-only corrections**: Admins can edit/remove Locations (buildings, floors, rooms) and can correct an
  already-submitted inspection's result/remarks/defect fields — inspectors and supervisors cannot. Every
  correction requires a stated reason and is written to the audit log with the before/after values. Defect
  status updates (open → assigned → resolved → verified) are also admin-only, since defects originate from
  inspector findings. This matches the spec's "historical records are immutable except for controlled,
  logged admin corrections" principle.
- **Inspection assignment**: Supervisors can assign a batch of equipment to an inspector with a due date.
- **Notifications**: in-app due-soon/due-today/overdue/defect/assignment/approval notifications, generated by
  a background job and refreshable on demand. Architecture is a single `notifications` table so email/SMS/
  push channels can be added later without changing the data model.
- **Dashboard**: total assets by type/status, compliance %, overdue/defective/due-within-30-days counts, plus
  charts (status breakdown, equipment by type, equipment by building, inspections per month).
- **Reports**: Equipment / Defect / Maintenance reports as CSV or Excel, and a Monthly Inspection Summary as PDF.
- **Bulk import**: Admins can bulk-create equipment from a CSV or Excel file on the Reports page — the
  counterpart to the export reports. A downloadable template shows the expected columns; buildings, floors,
  and rooms named in the file are matched by name or created automatically, so a new site's full inventory
  can be set up in one upload instead of one asset at a time. Each row is processed independently (a bad row
  is reported with a specific error, without blocking the rest of the file), and QR codes/barcodes are
  generated for every imported asset just like a manually-created one. This only creates new assets — it
  doesn't update existing ones by re-import.
- **Full inspection/maintenance/defect/photo history** per asset, shown as timelines on the asset detail page.
- **Audit log**: every create/update/approval action is recorded with who, when, and old/new values; read-only
  in the UI.
- **Settings**: due-soon threshold and per-equipment-type inspection intervals are editable by Admins.
- **PWA**: installable, app shell cached for offline use; inspection submissions made while offline are queued
  in `localStorage` and flushed automatically when connectivity returns (see "What's partial" below).
- **Tests**: pytest suite covering auth/permissions, asset creation/search/QR generation, the inspection →
  status → defect pipeline, and maintenance history immutability.

## What's partial (and why)

Per the brief's instruction to implement the closest functional version of anything that can't be fully built
here, rather than a fake placeholder:

- **Offline mode** covers the single most important field scenario — submitting a completed inspection while
  offline — via a `localStorage` queue that flushes on reconnect. It is not a full IndexedDB-backed sync engine
  covering every entity type; that's the natural next step (see section 8 below).
- **Email/browser push notifications** are not wired to a real provider. The `Notification` table and service
  are deliberately structured so a channel dispatcher (SendGrid, SES, web-push, etc.) can be added by reading
  from the same table/event calls, without a data model change.
- **SMS/WhatsApp** notifications are not implemented, matching the spec's "keep it modular so this can be added
  later" instruction.
- **Interactive map view** (section 43 of the spec) is not built, but the location model (building → floor →
  room/area with optional lat/lng and a `floor_plan_reference` field) is already shaped to support it later.
- **AI features** (section 42) are intentionally out of scope for this MVP, as instructed.

Nothing in the app is a fake button — every action shown performs a real API call.

---

## 3. Requirements

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional, for the production-style run)

## 4. Local development (no Docker)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults to a local SQLite file — no DB setup needed

# Apply migrations (creates all tables)
alembic upgrade head

# Load realistic demo data (3 buildings, 30 assets, sample inspections/defects/maintenance, 4 demo users)
python -m app.seed

# Run the API
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app is now at `http://localhost:5173` (Vite dev server proxies `/api` and `/static` to `http://localhost:8000`).

### Demo credentials (created by `python -m app.seed`)

| Role       | Email                      | Password        |
|------------|-----------------------------|------------------|
| Admin      | admin@fireaims.demo        | Admin@123        |
| Supervisor | supervisor@fireaims.demo   | Supervisor@123   |
| Inspector  | inspector1@fireaims.demo   | Inspector@123    |
| Inspector  | inspector2@fireaims.demo   | Inspector@123    |

## 5. Running tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Tests run against an isolated temporary SQLite database and don't touch your dev database.

## 6. Database migrations

Alembic is configured in `backend/alembic/`, pointed at the same `DATABASE_URL` the app uses.

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

The initial migration (`alembic/versions/*_initial_schema.py`) creates every table. `app/main.py` also calls
`Base.metadata.create_all()` on startup as a convenience for quick local/demo runs — in a real deployment, rely
on `alembic upgrade head` (as `docker-compose.yml` does) instead.

## 7. Docker / production-style run

```bash
docker compose up --build
```

This starts PostgreSQL, runs `alembic upgrade head`, then starts the backend on port 8000 and the frontend
(built and served via nginx, which also proxies `/api` and `/static` to the backend) on port 80.

Load demo data into the Postgres container:

```bash
docker compose exec backend python -m app.seed
```

Set a real `SECRET_KEY` via an `.env` file next to `docker-compose.yml` before deploying anywhere real:

```
SECRET_KEY=<a long random string>
```

## 7b. Deploying on Railway

Railway runs the backend and frontend as two separate services with two separate public URLs, which is
different from docker-compose's single shared origin — a few settings matter because of that:

1. **Postgres** — in your Railway project, "+ New" → Database → Add PostgreSQL. Railway provisions it and
   exposes a `DATABASE_URL` reference variable other services can use.

2. **Backend service** — "+ New" → GitHub Repo → this repo. In Settings:
   - **Root Directory**: `backend`
   - **Variables**: `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` (Railway's variable-reference syntax,
     picked from the dropdown when you type `${{`), `SECRET_KEY` = a long random string, `ENV` = `production`
   - Railway builds from `backend/Dockerfile` automatically. Its `start.sh` entrypoint runs
     `alembic upgrade head` before starting the server and binds to Railway's dynamic `$PORT` — no extra
     start-command override needed.
   - **Networking** → Generate Domain, so the service gets a public URL (e.g.
     `fire-aims-backend-production.up.railway.app`). Railway should default this domain's target port to
     8000 (matching `EXPOSE 8000` in `backend/Dockerfile`) — double check it if login later fails with a
     "can't reach the server" style error. Copy the domain URL for the next step.
   - **Storage** → Add a Volume mounted at `/app/static`. Without this, generated QR codes/barcodes and
     uploaded inspection photos are lost on every redeploy, since Railway's container filesystem is
     otherwise ephemeral.
   - Once it's deployed, run the seed script from Railway's shell for that service (or its CLI:
     `railway run python -m app.seed`) to load demo data.

3. **Frontend service** — "+ New" → GitHub Repo → this repo again, as a second service. In Settings:
   - **Root Directory**: `frontend`
   - **Build Variables** (not regular runtime Variables — Vite inlines this at build time, so it has to be
     set where Railway applies Docker build args): `VITE_API_URL` = the backend's public URL from step 2,
     no trailing slash (e.g. `https://fire-aims-backend-production.up.railway.app`)
   - **Networking** → Generate Domain for the frontend's own public URL — this is the one you actually share
     with inspectors/supervisors. This domain's target port must be **80** (nginx), not 8000 — Railway
     sometimes defaults it to whatever port a sibling service used, so check this explicitly if the page
     loads blank or the domain doesn't respond.

The backend's CORS is already configured to accept any origin (`app/core/config.py`), so no backend change
is needed to allow the frontend's Railway domain to call it.

## 8. Suggested next steps for a real deployment

- Swap the in-app QR payload scheme (`fireaims://scan/<asset_id>`) for a real HTTPS URL once the app has a
  production domain, so scanning with any phone camera (not just the in-app scanner) opens the asset page.
- Add an email/push notification channel dispatcher reading from the `notifications` table.
- Extend the offline queue to cover asset edits and maintenance records, not just inspection submissions, and
  back it with IndexedDB instead of `localStorage` for larger queues.
- Add the interactive building/floor map view described in the spec, using the existing `latitude`/`longitude`
  and `floor_plan_reference` fields already on the location and asset models.
- Put `backend/static/uploads` and `backend/static/qr` on object storage (S3-compatible) instead of local disk
  before running multiple backend replicas.

## 9. Important note on compliance

FIRE-AIMS helps a department track, schedule, and document fire safety equipment inspections and maintenance.
It does not itself certify or guarantee regulatory compliance — inspection checklist content and service
intervals are configurable specifically because actual requirements vary by jurisdiction, equipment
manufacturer instructions, and department SOPs, and should be set by someone qualified to do so for your
department.
