from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import require_admin_or_supervisor
from app.models.user import User
from app.models.records import AuditLog
from app.schemas.records import AuditLogOut

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(entity_type: Optional[str] = None, limit: int = 200,
                     db: Session = Depends(get_db), current_user: User = Depends(require_admin_or_supervisor)):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    return q.order_by(AuditLog.created_at.desc()).limit(limit).all()
