from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetStatus
from app.models.inspection import Inspection, InspectionResult
from app.models.records import Defect, DefectStatus, DefectSeverity, MaintenanceRecord
from app.models.location import Building

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_assets = db.query(Asset).count()

    by_type = {
        t.value: db.query(Asset).filter(Asset.asset_type == t).count() for t in AssetType
    }
    by_status = {
        s.value: db.query(Asset).filter(Asset.status == s).count() for s in AssetStatus
    }

    compliant = by_status.get(AssetStatus.COMPLIANT.value, 0)
    compliance_pct = round((compliant / total_assets) * 100, 1) if total_assets else 0.0

    open_defects = db.query(Defect).filter(Defect.status.notin_([DefectStatus.RESOLVED, DefectStatus.VERIFIED])).count()
    critical_defects = db.query(Defect).filter(
        Defect.status.notin_([DefectStatus.RESOLVED, DefectStatus.VERIFIED]),
        Defect.severity == DefectSeverity.CRITICAL,
    ).count()

    due_within_30 = db.query(Asset).filter(
        Asset.next_inspection_date.isnot(None),
        Asset.next_inspection_date <= datetime.utcnow() + timedelta(days=30),
        Asset.next_inspection_date >= datetime.utcnow(),
    ).count()

    return {
        "total_assets": total_assets,
        "by_type": by_type,
        "by_status": by_status,
        "compliance_percentage": compliance_pct,
        "overdue": by_status.get(AssetStatus.OVERDUE.value, 0),
        "defective": by_status.get(AssetStatus.DEFECTIVE.value, 0),
        "due_within_30_days": due_within_30,
        "open_defects": open_defects,
        "critical_defects": critical_defects,
        "total_buildings": db.query(Building).count(),
    }


@router.get("/analytics")
def dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    by_building = _equipment_by_building(db)

    # Inspections per month (last 6 months)
    inspections = db.query(Inspection).all()
    monthly = {}
    for insp in inspections:
        key = insp.inspected_at.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + 1
    inspections_per_month = [{"month": k, "count": v} for k, v in sorted(monthly.items())][-6:]

    failed_inspections = db.query(Inspection).filter(Inspection.overall_result == InspectionResult.FAILED).count()
    overdue_count = db.query(Asset).filter(Asset.status == AssetStatus.OVERDUE).count()
    maintenance_count = db.query(MaintenanceRecord).count()

    defects_by_severity = {
        sev.value: db.query(Defect).filter(Defect.severity == sev).count() for sev in DefectSeverity
    }

    return {
        "equipment_by_building": by_building,
        "inspections_per_month": inspections_per_month,
        "failed_inspections": failed_inspections,
        "overdue_count": overdue_count,
        "maintenance_activities": maintenance_count,
        "defects_by_severity": defects_by_severity,
    }


def _equipment_by_building(db: Session):
    from app.models.location import Location, Floor
    rows = (
        db.query(Building.name, func.count(Asset.id))
        .select_from(Building)
        .join(Floor, Floor.building_id == Building.id)
        .join(Location, Location.floor_id == Floor.id)
        .join(Asset, Asset.location_id == Location.id)
        .group_by(Building.name)
        .all()
    )
    return [{"building": name, "count": count} for name, count in rows]
