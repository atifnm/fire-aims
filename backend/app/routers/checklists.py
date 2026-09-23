from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.checklist import ChecklistTemplate, ChecklistTemplateItem
from app.schemas.inspection import ChecklistTemplateOut, ChecklistTemplateCreate
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api/checklists", tags=["checklists"])


@router.get("", response_model=List[ChecklistTemplateOut])
def list_checklists(asset_type: Optional[str] = None, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    q = db.query(ChecklistTemplate).filter(ChecklistTemplate.is_active == True)  # noqa: E712
    if asset_type:
        q = q.filter(ChecklistTemplate.asset_type == asset_type)
    return q.all()


@router.get("/{template_id}", response_model=ChecklistTemplateOut)
def get_checklist(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return t


@router.post("", response_model=ChecklistTemplateOut)
def create_checklist(payload: ChecklistTemplateCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_admin)):
    t = ChecklistTemplate(name=payload.name, asset_type=payload.asset_type)
    db.add(t)
    db.commit()
    db.refresh(t)
    for item in payload.items:
        db.add(ChecklistTemplateItem(template_id=t.id, **item.model_dump()))
    db.commit()
    db.refresh(t)
    log_audit(db, current_user.id, f"Admin created checklist template '{t.name}'", "checklist", t.id)
    return t


@router.put("/{template_id}", response_model=ChecklistTemplateOut)
def update_checklist(template_id: int, payload: ChecklistTemplateCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_admin)):
    t = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Checklist not found")
    t.name = payload.name
    t.asset_type = payload.asset_type
    # Replace items wholesale (admin is editing the full checklist configuration)
    db.query(ChecklistTemplateItem).filter(ChecklistTemplateItem.template_id == t.id).delete()
    for item in payload.items:
        db.add(ChecklistTemplateItem(template_id=t.id, **item.model_dump()))
    db.commit()
    db.refresh(t)
    log_audit(db, current_user.id, f"Admin updated checklist template '{t.name}'", "checklist", t.id)
    return t


@router.delete("/{template_id}")
def delete_checklist(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    t = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Checklist not found")
    t.is_active = False
    db.commit()
    log_audit(db, current_user.id, f"Admin deactivated checklist template '{t.name}'", "checklist", t.id)
    return {"detail": "Deactivated"}
