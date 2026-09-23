"""
Notification and audit-logging helpers.

Notification architecture is intentionally simple (DB row = in-app notification)
so that email/SMS/WhatsApp/push channels can be plugged in later by adding a
"channel" dispatcher that reads from the same Notification table/event calls.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus
from app.models.records import Notification, NotificationType, AuditLog
from app.services.status_service import get_due_soon_days


def create_notification(db: Session, type_: NotificationType, message: str,
                         asset_id: int = None, user_id: int = None, commit: bool = True):
    note = Notification(type=type_, message=message, asset_id=asset_id, user_id=user_id)
    db.add(note)
    if commit:
        db.commit()
        db.refresh(note)
    return note


def generate_due_date_notifications(db: Session):
    """
    Scans all assets and creates notifications for items that are due-soon (30/7/1 day
    milestones), due today, or overdue. Intended to be run on a schedule (see main.py
    APScheduler job) or on-demand from a dashboard refresh.
    """
    now = datetime.utcnow()
    due_soon_days = get_due_soon_days(db)
    milestones = sorted(set([due_soon_days, 7, 1]), reverse=True)

    assets = db.query(Asset).filter(Asset.next_inspection_date.isnot(None)).all()
    created = 0
    for asset in assets:
        delta_days = (asset.next_inspection_date.date() - now.date()).days
        message = None
        ntype = None
        if delta_days < 0:
            message = f"{asset.asset_id} inspection is OVERDUE by {abs(delta_days)} day(s)."
            ntype = NotificationType.OVERDUE
        elif delta_days == 0:
            message = f"{asset.asset_id} inspection is due TODAY."
            ntype = NotificationType.DUE_TODAY
        elif delta_days in milestones:
            message = f"{asset.asset_id} inspection due in {delta_days} day(s)."
            ntype = NotificationType.DUE_SOON

        if message:
            # avoid duplicate notifications for the same asset/message on the same day
            existing = (
                db.query(Notification)
                .filter(Notification.asset_id == asset.id, Notification.message == message)
                .first()
            )
            if not existing:
                create_notification(db, ntype, message, asset_id=asset.id, commit=False)
                created += 1
    db.commit()
    return created


def log_audit(db: Session, user_id: int, action: str, entity_type: str = None,
               entity_id: str = None, previous_value: str = None, new_value: str = None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        previous_value=previous_value,
        new_value=new_value,
    )
    db.add(entry)
    db.commit()
    return entry
