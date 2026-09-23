from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin_or_supervisor
from app.models.user import User
from app.models.asset import Asset, AssetStatus
from app.models.records import MaintenanceRecord
from app.schemas.records import MaintenanceCreate, MaintenanceOut
from app.services.status_service import recalculate_asset_status
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("", response_model=List[MaintenanceOut])
def list_maintenance(asset_id: Optional[int] = None, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    q = db.query(MaintenanceRecord)
    if asset_id:
        q = q.filter(MaintenanceRecord.asset_id == asset_id)
    return q.order_by(MaintenanceRecord.service_date.desc()).all()


@router.post("", response_model=MaintenanceOut)
def create_maintenance(payload: MaintenanceCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(require_admin_or_supervisor)):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    record = MaintenanceRecord(recorded_by_id=current_user.id, **payload.model_dump())
    db.add(record)

    # Maintenance always creates a new history row; it never overwrites prior records.
    from datetime import datetime
    asset.last_service_date = datetime.combine(payload.service_date, datetime.min.time())
    if payload.next_service_date:
        asset.next_service_date = datetime.combine(payload.next_service_date, datetime.min.time())

    # Completing maintenance takes the asset out of UNDER_MAINTENANCE/DEFECTIVE back into the date engine.
    if asset.status in (AssetStatus.UNDER_MAINTENANCE, AssetStatus.DEFECTIVE, AssetStatus.OUT_OF_SERVICE):
        asset.status = AssetStatus.COMPLIANT

    db.commit()
    recalculate_asset_status(db, asset)
    db.refresh(record)

    log_audit(db, current_user.id, f"Maintenance ({payload.service_type.value}) recorded on {asset.asset_id}",
              "maintenance", record.id)
    return record
