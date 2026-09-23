from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.records import Notification
from app.schemas.records import NotificationOut
from app.services.notification_service import generate_due_date_notifications

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Notification)
    if current_user.role == UserRole.INSPECTOR:
        q = q.filter(Notification.user_id == current_user.id)
    else:
        # Admins/supervisors see their own targeted notifications plus system-wide broadcasts.
        q = q.filter(or_(Notification.user_id == current_user.id, Notification.user_id.is_(None)))
    return q.order_by(Notification.created_at.desc()).limit(200).all()


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Notification).filter(Notification.id == notification_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = 1
    db.commit()
    return {"detail": "marked read"}


@router.post("/refresh")
def refresh_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Manually trigger a scan for due-soon/due-today/overdue notifications (also runs on a schedule)."""
    created = generate_due_date_notifications(db)
    return {"created": created}
