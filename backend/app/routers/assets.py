import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import pandas as pd

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetStatus, ASSET_PREFIX
from app.models.location import Building, Floor, Location
from app.models.asset_details import (
    ExtinguisherDetail, HoseCabinetDetail, HoseReelDetail, BranchDetail, McpDetail,
)
from app.models.inspection import Inspection
from app.models.records import MaintenanceRecord, Defect, Photo
from app.schemas.asset import AssetCreate, AssetUpdate, AssetOut
from app.schemas.inspection import InspectionOut
from app.schemas.records import MaintenanceOut, DefectOut
from app.services.qr_service import generate_qr_code, generate_barcode
from app.services.status_service import recalculate_asset_status
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api/assets", tags=["assets"])

DETAIL_MODEL_MAP = {
    AssetType.EXTINGUISHER: ("extinguisher_detail", ExtinguisherDetail),
    AssetType.HOSE_CABINET: ("hose_cabinet_detail", HoseCabinetDetail),
    AssetType.HOSE_REEL: ("hose_reel_detail", HoseReelDetail),
    AssetType.BRANCH: ("branch_detail", BranchDetail),
    AssetType.MCP: ("mcp_detail", McpDetail),
}


def _next_asset_number(db: Session, asset_type: AssetType) -> str:
    prefix = ASSET_PREFIX[asset_type]
    count = db.query(Asset).filter(Asset.asset_type == asset_type).count()
    candidate_num = count + 1
    while True:
        candidate = f"{prefix}-{candidate_num:05d}"
        exists = db.query(Asset).filter(Asset.asset_id == candidate).first()
        if not exists:
            return candidate
        candidate_num += 1


def _serialize(asset: Asset) -> AssetOut:
    out = AssetOut.model_validate(asset)
    out.location_path = asset.location_path
    return out


@router.get("", response_model=List[AssetOut])
def list_assets(
    building_id: Optional[int] = None,
    floor_id: Optional[int] = None,
    location_id: Optional[int] = None,
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    search: Optional[str] = Query(None, description="search asset_id, serial number, manufacturer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Asset)
    if asset_type:
        q = q.filter(Asset.asset_type == asset_type)
    if status:
        q = q.filter(Asset.status == status)
    if location_id:
        q = q.filter(Asset.location_id == location_id)
    if floor_id or building_id:
        from app.models.location import Location, Floor
        q = q.join(Location, Asset.location_id == Location.id).join(Floor, Location.floor_id == Floor.id)
        if floor_id:
            q = q.filter(Floor.id == floor_id)
        if building_id:
            q = q.filter(Floor.building_id == building_id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Asset.asset_id.ilike(like), Asset.serial_number.ilike(like),
                          Asset.manufacturer.ilike(like)))
    assets = q.order_by(Asset.asset_id).all()
    return [_serialize(a) for a in assets]


@router.get("/{asset_id_or_code}", response_model=AssetOut)
def get_asset(asset_id_or_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = _find_asset(db, asset_id_or_code)
    return _serialize(asset)


@router.get("/scan/{asset_code}", response_model=AssetOut)
def scan_asset(asset_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Resolve a scanned QR/barcode payload (the human asset_id) to the full asset record."""
    asset = db.query(Asset).filter(Asset.asset_id == asset_code).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"No asset found for code '{asset_code}'")
    return _serialize(asset)


def _find_asset(db: Session, asset_id_or_code: str) -> Asset:
    asset = None
    if asset_id_or_code.isdigit():
        asset = db.query(Asset).filter(Asset.id == int(asset_id_or_code)).first()
    if not asset:
        asset = db.query(Asset).filter(Asset.asset_id == asset_id_or_code).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def _apply_detail(db: Session, asset: Asset, payload: AssetCreate | AssetUpdate):
    field_name, model_cls = DETAIL_MODEL_MAP[asset.asset_type]
    detail_payload = getattr(payload, field_name, None)
    if detail_payload is None:
        return
    existing = getattr(asset, field_name, None)
    data = detail_payload.model_dump(exclude_unset=True)
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
    else:
        new_detail = model_cls(asset_id=asset.id, **data)
        db.add(new_detail)


@router.post("", response_model=AssetOut)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    asset_code = _next_asset_number(db, payload.asset_type)
    data = payload.model_dump(exclude={
        "extinguisher_detail", "hose_cabinet_detail", "hose_reel_detail", "branch_detail", "mcp_detail",
    })
    asset = Asset(asset_id=asset_code, **data)
    db.add(asset)
    db.commit()
    db.refresh(asset)

    _apply_detail(db, asset, payload)
    db.commit()

    # Generate QR + barcode immediately
    asset.qr_code_path = generate_qr_code(asset.asset_id)
    asset.barcode_path = generate_barcode(asset.asset_id)
    db.commit()

    recalculate_asset_status(db, asset)
    db.refresh(asset)

    log_audit(db, current_user.id, f"Admin created asset {asset.asset_id}", "asset", asset.id)
    return _serialize(asset)


# ---- Bulk import (CSV/Excel) ----

IMPORT_COLUMNS = [
    "asset_type", "building", "floor", "room", "area", "specific_location",
    "manufacturer", "model", "serial_number", "installation_date", "assigned_department", "remarks",
    "extinguisher_type", "capacity", "hose_length_m", "hose_diameter_mm",
    "nozzle_type", "condition", "connected_panel", "zone_address", "cabinet_material",
]


@router.get("/import/template")
def download_import_template(current_user: User = Depends(require_admin)):
    """A blank CSV with the exact columns the bulk importer understands, plus one example row."""
    example = {
        "asset_type": "extinguisher", "building": "Fire Station HQ", "floor": "Ground Floor",
        "room": "Electrical Room", "area": "Near Main Entrance", "specific_location": "",
        "manufacturer": "Amerex", "model": "B500", "serial_number": "SN-100234",
        "installation_date": "2025-01-15", "assigned_department": "Facilities", "remarks": "",
        "extinguisher_type": "ABC Dry Chemical", "capacity": "9kg", "hose_length_m": "",
        "hose_diameter_mm": "", "nozzle_type": "", "condition": "", "connected_panel": "",
        "zone_address": "", "cabinet_material": "",
    }
    df = pd.DataFrame([example], columns=IMPORT_COLUMNS)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asset_import_template.csv"},
    )


def _get_or_create_building(db: Session, name: str) -> Building:
    b = db.query(Building).filter(Building.name.ilike(name.strip())).first()
    if not b:
        b = Building(name=name.strip())
        db.add(b)
        db.flush()
    return b


def _get_or_create_floor(db: Session, building: Building, name: str) -> Floor:
    f = db.query(Floor).filter(Floor.building_id == building.id, Floor.name.ilike(name.strip())).first()
    if not f:
        f = Floor(building_id=building.id, name=name.strip())
        db.add(f)
        db.flush()
    return f


def _get_or_create_location(db: Session, floor: Floor, room: str, area: str) -> Location:
    q = db.query(Location).filter(Location.floor_id == floor.id)
    q = q.filter(Location.room.ilike(room.strip())) if room else q.filter(Location.room.is_(None))
    q = q.filter(Location.area.ilike(area.strip())) if area else q.filter(Location.area.is_(None))
    loc = q.first()
    if not loc:
        loc = Location(floor_id=floor.id, room=room.strip() if room else None, area=area.strip() if area else None)
        db.add(loc)
        db.flush()
    return loc


def _clean(value):
    """Normalize a pandas cell to a plain string or None (pandas gives NaN for blank cells)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip()
    return s if s else None


def _import_one_row(db: Session, row: dict) -> str:
    """Creates one asset from an import row. Returns the new asset_id. Raises ValueError on bad input."""
    asset_type_raw = _clean(row.get("asset_type"))
    if not asset_type_raw:
        raise ValueError("asset_type is required")
    try:
        asset_type = AssetType(asset_type_raw.strip().lower())
    except ValueError:
        raise ValueError(
            f"invalid asset_type '{asset_type_raw}' — must be one of: {', '.join(t.value for t in AssetType)}"
        )

    location_id = None
    building_name, floor_name = _clean(row.get("building")), _clean(row.get("floor"))
    room, area = _clean(row.get("room")), _clean(row.get("area"))
    if building_name and floor_name:
        building = _get_or_create_building(db, building_name)
        floor = _get_or_create_floor(db, building, floor_name)
        if room or area:
            location = _get_or_create_location(db, floor, room, area)
            location_id = location.id

    installation_date = None
    raw_date = _clean(row.get("installation_date"))
    if raw_date:
        try:
            installation_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"installation_date '{raw_date}' must be in YYYY-MM-DD format")

    asset_code = _next_asset_number(db, asset_type)
    asset = Asset(
        asset_id=asset_code,
        asset_type=asset_type,
        location_id=location_id,
        specific_location=_clean(row.get("specific_location")),
        manufacturer=_clean(row.get("manufacturer")),
        model=_clean(row.get("model")),
        serial_number=_clean(row.get("serial_number")),
        installation_date=installation_date,
        assigned_department=_clean(row.get("assigned_department")),
        remarks=_clean(row.get("remarks")),
    )
    db.add(asset)
    db.flush()

    if asset_type == AssetType.EXTINGUISHER:
        db.add(ExtinguisherDetail(
            asset_id=asset.id,
            extinguisher_type=_clean(row.get("extinguisher_type")) or "ABC Dry Chemical",
            capacity=_clean(row.get("capacity")),
        ))
    elif asset_type == AssetType.HOSE_CABINET:
        db.add(HoseCabinetDetail(asset_id=asset.id, cabinet_material=_clean(row.get("cabinet_material"))))
    elif asset_type == AssetType.HOSE_REEL:
        hl = _clean(row.get("hose_length_m"))
        hd = _clean(row.get("hose_diameter_mm"))
        db.add(HoseReelDetail(
            asset_id=asset.id,
            hose_length_m=float(hl) if hl else None,
            hose_diameter_mm=float(hd) if hd else None,
        ))
    elif asset_type == AssetType.BRANCH:
        db.add(BranchDetail(
            asset_id=asset.id, nozzle_type=_clean(row.get("nozzle_type")), condition=_clean(row.get("condition")),
        ))
    elif asset_type == AssetType.MCP:
        db.add(McpDetail(
            asset_id=asset.id, connected_panel=_clean(row.get("connected_panel")),
            zone_address=_clean(row.get("zone_address")),
        ))

    db.flush()
    asset.qr_code_path = generate_qr_code(asset.asset_id)
    asset.barcode_path = generate_barcode(asset.asset_id)
    recalculate_asset_status(db, asset, commit=False)
    return asset.asset_id


@router.post("/import")
async def import_assets(file: UploadFile = File(...), db: Session = Depends(get_db),
                         current_user: User = Depends(require_admin)):
    """
    Bulk-create fire safety equipment from a CSV or Excel file (columns per /assets/import/template).
    Buildings/floors/rooms named in the sheet are matched by name or created automatically. Each row
    becomes one new asset with an auto-generated Asset ID, QR code, and barcode — this endpoint only
    creates new assets, it does not update existing ones. Every row is processed independently: a bad
    row is reported in the results without blocking the rest of the file.
    """
    filename = (file.filename or "").lower()
    contents = await file.read()
    try:
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(contents), dtype=str)
        else:
            df = pd.read_csv(io.BytesIO(contents), dtype=str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")

    df.columns = [str(c).strip().lower() for c in df.columns]
    if "asset_type" not in df.columns:
        raise HTTPException(status_code=400, detail="File is missing the required 'asset_type' column")

    results = []
    created = 0
    for idx, row in df.iterrows():
        row_num = idx + 2  # +1 for zero-index, +1 for the header row, matching what a spreadsheet shows
        row_dict = row.to_dict()
        try:
            with db.begin_nested():
                asset_id = _import_one_row(db, row_dict)
            created += 1
            results.append({"row": row_num, "asset_id": asset_id, "status": "created", "error": None})
        except Exception as e:
            # db.begin_nested()'s context manager already rolled back to the row's own
            # SAVEPOINT on exception — do NOT call db.rollback() here, that would roll back
            # the whole batch (including rows already committed-pending in this transaction).
            results.append({"row": row_num, "asset_id": None, "status": "failed", "error": str(e)})

    db.commit()

    log_audit(
        db, current_user.id,
        f"Admin bulk-imported assets from '{file.filename}': {created} created, {len(results) - created} failed",
        "asset", None,
    )

    return {"total": len(results), "created": created, "failed": len(results) - created, "results": results}


@router.put("/{asset_id_or_code}", response_model=AssetOut)
def update_asset(asset_id_or_code: str, payload: AssetUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_admin)):
    asset = _find_asset(db, asset_id_or_code)
    data = payload.model_dump(exclude_unset=True, exclude={
        "extinguisher_detail", "hose_cabinet_detail", "hose_reel_detail", "branch_detail", "mcp_detail",
    })
    previous = f"status={asset.status}"
    for field, value in data.items():
        setattr(asset, field, value)
    _apply_detail(db, asset, payload)
    db.commit()
    recalculate_asset_status(db, asset)
    db.refresh(asset)
    log_audit(db, current_user.id, f"Admin updated asset {asset.asset_id}", "asset", asset.id,
              previous_value=previous, new_value=f"status={asset.status}")
    return _serialize(asset)


@router.delete("/{asset_id_or_code}")
def delete_asset(asset_id_or_code: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    asset = _find_asset(db, asset_id_or_code)
    code = asset.asset_id
    db.delete(asset)
    db.commit()
    log_audit(db, current_user.id, f"Admin deleted asset {code}", "asset", asset_id_or_code)
    return {"detail": "Deleted"}


@router.post("/{asset_id_or_code}/regenerate-codes", response_model=AssetOut)
def regenerate_codes(asset_id_or_code: str, db: Session = Depends(get_db),
                      current_user: User = Depends(require_admin)):
    asset = _find_asset(db, asset_id_or_code)
    asset.qr_code_path = generate_qr_code(asset.asset_id)
    asset.barcode_path = generate_barcode(asset.asset_id)
    db.commit()
    db.refresh(asset)
    return _serialize(asset)


@router.get("/{asset_id_or_code}/history")
def asset_history(asset_id_or_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = _find_asset(db, asset_id_or_code)
    inspections = (
        db.query(Inspection).filter(Inspection.asset_id == asset.id).order_by(Inspection.inspected_at.desc()).all()
    )
    maintenance = (
        db.query(MaintenanceRecord).filter(MaintenanceRecord.asset_id == asset.id)
        .order_by(MaintenanceRecord.service_date.desc()).all()
    )
    defects = db.query(Defect).filter(Defect.asset_id == asset.id).order_by(Defect.created_at.desc()).all()
    photos = db.query(Photo).filter(Photo.asset_id == asset.id).order_by(Photo.uploaded_at.desc()).all()

    return {
        "asset": _serialize(asset),
        "inspections": [InspectionOut.model_validate(i) for i in inspections],
        "maintenance": [MaintenanceOut.model_validate(m) for m in maintenance],
        "defects": [DefectOut.model_validate(d) for d in defects],
        "photos": [{"id": p.id, "file_path": p.file_path, "context": p.context,
                    "uploaded_at": p.uploaded_at} for p in photos],
    }
