"""
Automatic asset status calculation.

Rules (see Settings for configurable thresholds):
- If asset has an unresolved defect with severity HIGH/CRITICAL -> DEFECTIVE
- If asset.status is manually set to UNDER_MAINTENANCE / OUT_OF_SERVICE, leave it
  (those are operator-controlled states, not date-driven)
- Else based on next_inspection_date vs today + due_soon_days threshold:
    overdue -> OVERDUE
    today -> DUE_TODAY
    within due_soon_days -> DUE_SOON
    else -> COMPLIANT
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus
from app.models.records import Defect, DefectStatus, DefectSeverity, AppSetting


def get_due_soon_days(db: Session) -> int:
    setting = db.query(AppSetting).filter(AppSetting.key == "due_soon_days").first()
    if setting:
        try:
            return int(setting.value)
        except ValueError:
            pass
    return 30


def recalculate_asset_status(db: Session, asset: Asset, commit: bool = True) -> AssetStatus:
    # Manually-controlled states are not overridden by the date engine.
    if asset.status in (AssetStatus.UNDER_MAINTENANCE, AssetStatus.OUT_OF_SERVICE):
        return asset.status

    open_defect = (
        db.query(Defect)
        .filter(
            Defect.asset_id == asset.id,
            Defect.status.notin_([DefectStatus.RESOLVED, DefectStatus.VERIFIED]),
            Defect.severity.in_([DefectSeverity.HIGH, DefectSeverity.CRITICAL]),
        )
        .first()
    )
    if open_defect:
        asset.status = AssetStatus.DEFECTIVE
        if commit:
            db.add(asset)
            db.commit()
        return asset.status

    due_soon_days = get_due_soon_days(db)
    now = datetime.utcnow()

    if not asset.next_inspection_date:
        asset.status = AssetStatus.COMPLIANT
    else:
        delta_days = (asset.next_inspection_date.date() - now.date()).days
        if delta_days < 0:
            asset.status = AssetStatus.OVERDUE
        elif delta_days == 0:
            asset.status = AssetStatus.DUE_TODAY
        elif delta_days <= due_soon_days:
            asset.status = AssetStatus.DUE_SOON
        else:
            asset.status = AssetStatus.COMPLIANT

    if commit:
        db.add(asset)
        db.commit()
        db.refresh(asset)
    return asset.status


def recalculate_all_assets(db: Session):
    assets = db.query(Asset).all()
    for asset in assets:
        recalculate_asset_status(db, asset, commit=False)
    db.commit()
