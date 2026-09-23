from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.records import AppSetting
from app.schemas.records import AppSettingOut, AppSettingUpdate
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api/settings", tags=["settings"])

DEFAULT_SETTINGS = [
    ("due_soon_days", "30", "Days before next inspection date to mark an asset DUE SOON"),
    ("interval_extinguisher_days", "30", "Default days between fire extinguisher inspections"),
    ("interval_hose_cabinet_days", "90", "Default days between hose cabinet inspections"),
    ("interval_hose_reel_days", "90", "Default days between hose reel inspections"),
    ("interval_branch_days", "90", "Default days between branch/nozzle inspections"),
    ("interval_mcp_days", "180", "Default days between MCP functional tests"),
    ("extinguisher_service_interval_days", "365", "Default days between extinguisher refill/service"),
]


@router.get("", response_model=List[AppSettingOut])
def list_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = {s.key for s in db.query(AppSetting).all()}
    for key, value, desc in DEFAULT_SETTINGS:
        if key not in existing:
            db.add(AppSetting(key=key, value=value, description=desc))
    db.commit()
    return db.query(AppSetting).order_by(AppSetting.key).all()


@router.put("/{key}", response_model=AppSettingOut)
def update_setting(key: str, payload: AppSettingUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(require_admin)):
    setting = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    previous = setting.value
    setting.value = payload.value
    db.commit()
    db.refresh(setting)
    log_audit(db, current_user.id, f"Admin changed setting '{key}'", "setting", key,
              previous_value=previous, new_value=payload.value)
    return setting
