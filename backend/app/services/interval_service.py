from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.asset import AssetType
from app.models.records import AppSetting

DEFAULT_INTERVALS = {
    AssetType.EXTINGUISHER: 30,
    AssetType.HOSE_CABINET: 90,
    AssetType.HOSE_REEL: 90,
    AssetType.BRANCH: 90,
    AssetType.MCP: 180,
}

SETTING_KEY_MAP = {
    AssetType.EXTINGUISHER: "interval_extinguisher_days",
    AssetType.HOSE_CABINET: "interval_hose_cabinet_days",
    AssetType.HOSE_REEL: "interval_hose_reel_days",
    AssetType.BRANCH: "interval_branch_days",
    AssetType.MCP: "interval_mcp_days",
}


def get_inspection_interval_days(db: Session, asset_type: AssetType) -> int:
    key = SETTING_KEY_MAP.get(asset_type)
    if key:
        setting = db.query(AppSetting).filter(AppSetting.key == key).first()
        if setting:
            try:
                return int(setting.value)
            except ValueError:
                pass
    return DEFAULT_INTERVALS.get(asset_type, 90)


def calculate_next_inspection_date(db: Session, asset_type: AssetType, from_date: datetime = None) -> datetime:
    from_date = from_date or datetime.utcnow()
    interval = get_inspection_interval_days(db, asset_type)
    return from_date + timedelta(days=interval)
