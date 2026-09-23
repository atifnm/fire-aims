from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_admin_or_supervisor
from app.models.user import User, UserRole
from app.models.asset import Asset, AssetStatus
from app.models.inspection import Inspection, InspectionItem, InspectionResult, InspectionStatus, InspectionAssignment
from app.models.records import Defect, DefectSeverity
from app.schemas.inspection import (
    InspectionCreate, InspectionOut, InspectionReview, InspectionAdminUpdate,
    InspectionAssignmentCreate, InspectionAssignmentOut,
)
from app.services.interval_service import calculate_next_inspection_date
from app.services.status_service import recalculate_asset_status
from app.services.notification_service import log_audit, create_notification
from app.models.records import NotificationType

router = APIRouter(prefix="/api/inspections", tags=["inspections"])


@router.get("", response_model=List[InspectionOut])
def list_inspections(
    asset_id: Optional[int] = None,
    inspector_id: Optional[int] = None,
    status: Optional[InspectionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Inspection)
    if asset_id:
        q = q.filter(Inspection.asset_id == asset_id)
    if inspector_id:
        q = q.filter(Inspection.inspector_id == inspector_id)
    if status:
        q = q.filter(Inspection.status == status)
    # Inspectors only see their own submissions; admins/supervisors see all.
    if current_user.role == UserRole.INSPECTOR:
        q = q.filter(Inspection.inspector_id == current_user.id)
    return q.order_by(Inspection.inspected_at.desc()).all()


@router.get("/{inspection_id}", response_model=InspectionOut)
def get_inspection(inspection_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return insp


@router.post("", response_model=InspectionOut)
def submit_inspection(payload: InspectionCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    now = datetime.utcnow()
    next_date = calculate_next_inspection_date(db, asset.asset_type, from_date=now)

    inspection = Inspection(
        asset_id=asset.id,
        inspector_id=current_user.id,
        checklist_template_id=payload.checklist_template_id,
        inspected_at=now,
        overall_result=payload.overall_result,
        general_remarks=payload.general_remarks,
        defect_description=payload.defect_description,
        corrective_action=payload.corrective_action,
        next_inspection_date=next_date,
        status=InspectionStatus.SUBMITTED,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    for item in payload.items:
        db.add(InspectionItem(inspection_id=inspection.id, **item.model_dump()))

    # Update the asset's own tracking fields (historical inspection rows remain immutable).
    asset.last_inspection_date = now
    asset.next_inspection_date = next_date

    # A failing/needs-maintenance result automatically opens a defect + corrective action record.
    if payload.overall_result in (InspectionResult.REQUIRES_MAINTENANCE, InspectionResult.FAILED) or payload.defect_description:
        severity = DefectSeverity(payload.defect_severity) if payload.defect_severity else (
            DefectSeverity.HIGH if payload.overall_result == InspectionResult.FAILED else DefectSeverity.MEDIUM
        )
        defect = Defect(
            asset_id=asset.id,
            inspection_id=inspection.id,
            description=payload.defect_description or f"Inspection result: {payload.overall_result.value}",
            severity=severity,
            corrective_action=payload.corrective_action,
        )
        db.add(defect)
        create_notification(
            db, NotificationType.DEFECT,
            f"Defect recorded on {asset.asset_id}: {defect.description[:120]}",
            asset_id=asset.id, commit=False,
        )

    if payload.overall_result == InspectionResult.FAILED:
        from app.models.asset import AssetStatus
        asset.status = AssetStatus.OUT_OF_SERVICE

    db.commit()
    recalculate_asset_status(db, asset)
    db.refresh(inspection)

    log_audit(db, current_user.id, f"Inspector {current_user.employee_code} completed inspection on {asset.asset_id}",
              "inspection", inspection.id, new_value=payload.overall_result.value)

    return inspection


@router.post("/{inspection_id}/review", response_model=InspectionOut)
def review_inspection(inspection_id: int, payload: InspectionReview, db: Session = Depends(get_db),
                       current_user: User = Depends(require_admin_or_supervisor)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    insp.status = InspectionStatus.APPROVED if payload.approve else InspectionStatus.RETURNED
    insp.reviewed_by_id = current_user.id
    insp.reviewed_at = datetime.utcnow()
    insp.review_notes = payload.review_notes
    db.commit()
    db.refresh(insp)

    verb = "approved" if payload.approve else "returned for correction"
    log_audit(db, current_user.id, f"Supervisor {verb} inspection #{insp.id}", "inspection", insp.id)
    create_notification(
        db, NotificationType.APPROVAL,
        f"Inspection #{insp.id} was {verb} by {current_user.full_name}.",
        asset_id=insp.asset_id, user_id=insp.inspector_id,
    )
    return insp


@router.put("/{inspection_id}", response_model=InspectionOut)
def correct_inspection(inspection_id: int, payload: InspectionAdminUpdate, db: Session = Depends(get_db),
                        current_user: User = Depends(require_admin)):
    """
    Admin-only correction of an inspection record submitted by an inspector (or reviewed by a
    supervisor). Inspectors and supervisors cannot call this - it exists specifically so an
    admin can fix a mis-entered result/remarks after the fact, per spec section 16: historical
    records are otherwise immutable, but admins may have controlled correction functionality,
    provided changes are logged. Every field changed is captured in the audit log with old/new
    values and the admin's stated reason.
    """
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    asset = db.query(Asset).filter(Asset.id == insp.asset_id).first()

    data = payload.model_dump(exclude_unset=True, exclude={"correction_reason"})
    if not data:
        raise HTTPException(status_code=400, detail="No fields to correct were provided")

    previous = {
        "overall_result": insp.overall_result.value if insp.overall_result else None,
        "general_remarks": insp.general_remarks,
        "defect_description": insp.defect_description,
        "corrective_action": insp.corrective_action,
        "next_inspection_date": insp.next_inspection_date.isoformat() if insp.next_inspection_date else None,
    }

    # Is this the asset's most recently recorded inspection? If so, correcting it should also
    # refresh the asset's own tracking fields (last/next inspection date, status) to match.
    is_latest = (
        asset is not None and asset.last_inspection_date is not None and insp.inspected_at is not None
        and abs((asset.last_inspection_date - insp.inspected_at).total_seconds()) < 60
    )

    for field, value in data.items():
        setattr(insp, field, value)
    db.commit()
    db.refresh(insp)

    if is_latest:
        if payload.next_inspection_date:
            asset.next_inspection_date = payload.next_inspection_date
        if payload.overall_result == InspectionResult.FAILED:
            asset.status = AssetStatus.OUT_OF_SERVICE
        db.commit()
        recalculate_asset_status(db, asset)

    new_values = {
        "overall_result": insp.overall_result.value if insp.overall_result else None,
        "general_remarks": insp.general_remarks,
        "defect_description": insp.defect_description,
        "corrective_action": insp.corrective_action,
        "next_inspection_date": insp.next_inspection_date.isoformat() if insp.next_inspection_date else None,
    }
    log_audit(
        db, current_user.id,
        f"Admin corrected inspection #{insp.id} on {asset.asset_id if asset else insp.asset_id} "
        f"— reason: {payload.correction_reason}",
        "inspection", insp.id,
        previous_value=str({k: v for k, v in previous.items() if k in data}),
        new_value=str({k: v for k, v in new_values.items() if k in data}),
    )
    return insp


# ---- Assignments ----
@router.get("/assignments/list", response_model=List[InspectionAssignmentOut])
def list_assignments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(InspectionAssignment)
    if current_user.role == UserRole.INSPECTOR:
        q = q.filter(InspectionAssignment.inspector_id == current_user.id)
    return q.order_by(InspectionAssignment.created_at.desc()).all()


@router.post("/assignments", response_model=InspectionAssignmentOut)
def create_assignment(payload: InspectionAssignmentCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(require_admin_or_supervisor)):
    assignment = InspectionAssignment(
        inspector_id=payload.inspector_id,
        assigned_by_id=current_user.id,
        building_id=payload.building_id,
        asset_ids_csv=",".join(payload.asset_ids),
        due_date=payload.due_date,
        notes=payload.notes,
        status="assigned",
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    create_notification(
        db, NotificationType.ASSIGNMENT,
        f"You have been assigned {len(payload.asset_ids) or 'building-wide'} inspection(s), due "
        f"{payload.due_date.date() if payload.due_date else 'soon'}.",
        user_id=payload.inspector_id,
    )
    log_audit(db, current_user.id, f"Assigned inspections to user #{payload.inspector_id}",
              "inspection_assignment", assignment.id)
    return assignment


@router.put("/assignments/{assignment_id}/status", response_model=InspectionAssignmentOut)
def update_assignment_status(assignment_id: int, new_status: str, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    assignment = db.query(InspectionAssignment).filter(InspectionAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.status = new_status
    db.commit()
    db.refresh(assignment)
    return assignment
