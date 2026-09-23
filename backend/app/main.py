from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app import models  # noqa: F401 - ensures all models are registered on Base.metadata
from app.services.notification_service import generate_due_date_notifications
from app.services.status_service import recalculate_all_assets

from app.routers import (
    auth, users, locations, assets, checklists, inspections,
    maintenance, defects, photos, notifications, audit, settings as settings_router, dashboard, reports,
)

app = FastAPI(
    title="FIRE-AIMS API",
    description="Fire Inspection, Recording & Equipment Asset Information Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup. For production, use Alembic migrations instead
# (see backend/alembic/) — this create_all is convenient for local/dev/demo runs.
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(assets.router)
app.include_router(checklists.router)
app.include_router(inspections.router)
app.include_router(maintenance.router)
app.include_router(defects.router)
app.include_router(photos.router)
app.include_router(notifications.router)
app.include_router(audit.router)
app.include_router(settings_router.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


scheduler = BackgroundScheduler()


def _scheduled_job():
    db = SessionLocal()
    try:
        recalculate_all_assets(db)
        generate_due_date_notifications(db)
    finally:
        db.close()


@app.on_event("startup")
def start_scheduler():
    # Runs once a day to recalculate asset statuses and generate due-date notifications.
    # This is the same logic exposed on-demand via POST /api/notifications/refresh.
    scheduler.add_job(_scheduled_job, "interval", hours=24, id="daily_status_scan", replace_existing=True)
    scheduler.start()


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown(wait=False)
