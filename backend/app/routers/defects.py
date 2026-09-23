from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.asset import Asset
from app.models.records import Defect, DefectStatus
from app.schemas.records import DefectCreate, DefectUpdate, DefectOut
from app.services.status_service import recalculate_asset_status
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api/defects", tags=["defects"])


@router.get("", response_model=List[DefectOut])
def list_defects(asset_id: Optional[int] = None, status: Optional[DefectStatus] = None,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Defect)
    if asset_id:
        q = q.filter(Defect.asset_id == asset_id)
    if status:
        q = q.filter(Defect.status == status)
    return q.order_by(Defect.created_at.desc()).all()


@router.post("", response_model=DefectOut)
def create_defect(payload: DefectCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    defect = Defect(**payload.model_dump())
    db.add(defect)
    db.commit()
    recalculate_asset_status(db, asset)
    db.refresh(defect)
    log_audit(db, current_user.id, f"Defect logged on {asset.asset_id}", "defect", defect.id)
    return defect


@router.put("/{defect_id}", response_model=DefectOut)
def update_defect(defect_id: int, payload: DefectUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(require_admin)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(defect, field, value)
    if payload.status in (DefectStatus.RESOLVED, DefectStatus.VERIFIED):
        defect.resolved_at = datetime.utcnow()
    db.commit()
    asset = db.query(Asset).filter(Asset.id == defect.asset_id).first()
    recalculate_asset_status(db, asset)
    db.refresh(defect)
    log_audit(db, current_user.id, f"Defect #{defect.id} updated", "defect", defect.id,
              new_value=str(payload.status.value) if payload.status else None)
    return defect
