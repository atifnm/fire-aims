from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.location import Building, Floor, Location
from app.schemas.location import (
    BuildingCreate, BuildingUpdate, BuildingOut,
    FloorCreate, FloorUpdate, FloorOut,
    LocationCreate, LocationUpdate, LocationOut,
)
from app.services.notification_service import log_audit

router = APIRouter(prefix="/api", tags=["locations"])


# ---- Buildings ----
@router.get("/buildings", response_model=List[BuildingOut])
def list_buildings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Building).order_by(Building.name).all()


@router.post("/buildings", response_model=BuildingOut)
def create_building(payload: BuildingCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_admin)):
    b = Building(**payload.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    log_audit(db, current_user.id, f"Admin created building {b.name}", "building", b.id)
    return b


@router.put("/buildings/{building_id}", response_model=BuildingOut)
def update_building(building_id: int, payload: BuildingUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_admin)):
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    previous = f"name={b.name}, code={b.code}, address={b.address}"
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(b, field, value)
    db.commit()
    db.refresh(b)
    log_audit(db, current_user.id, f"Admin edited building {b.name}", "building", b.id,
              previous_value=previous, new_value=f"name={b.name}, code={b.code}, address={b.address}")
    return b


@router.delete("/buildings/{building_id}")
def delete_building(building_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(b)
    db.commit()
    log_audit(db, current_user.id, f"Admin deleted building {b.name}", "building", building_id)
    return {"detail": "Deleted"}


# ---- Floors ----
@router.get("/floors", response_model=List[FloorOut])
def list_floors(building_id: int = None, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    q = db.query(Floor)
    if building_id:
        q = q.filter(Floor.building_id == building_id)
    return q.order_by(Floor.name).all()


@router.post("/floors", response_model=FloorOut)
def create_floor(payload: FloorCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    f = Floor(**payload.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    log_audit(db, current_user.id, f"Admin created floor {f.name}", "floor", f.id)
    return f


@router.put("/floors/{floor_id}", response_model=FloorOut)
def update_floor(floor_id: int, payload: FloorUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_admin)):
    f = db.query(Floor).filter(Floor.id == floor_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Floor not found")
    previous = f"name={f.name}, building_id={f.building_id}"
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(f, field, value)
    db.commit()
    db.refresh(f)
    log_audit(db, current_user.id, f"Admin edited floor {f.name}", "floor", f.id,
              previous_value=previous, new_value=f"name={f.name}, building_id={f.building_id}")
    return f


@router.delete("/floors/{floor_id}")
def delete_floor(floor_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    f = db.query(Floor).filter(Floor.id == floor_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Floor not found")
    db.delete(f)
    db.commit()
    log_audit(db, current_user.id, f"Admin deleted floor {f.name}", "floor", floor_id)
    return {"detail": "Deleted"}


# ---- Locations ----
@router.get("/locations", response_model=List[LocationOut])
def list_locations(floor_id: int = None, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    q = db.query(Location)
    if floor_id:
        q = q.filter(Location.floor_id == floor_id)
    results = q.all()
    out = []
    for loc in results:
        item = LocationOut.model_validate(loc)
        item.display_path = loc.display_path
        out.append(item)
    return out


@router.post("/locations", response_model=LocationOut)
def create_location(payload: LocationCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_admin)):
    loc = Location(**payload.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    log_audit(db, current_user.id, f"Admin created location #{loc.id}", "location", loc.id)
    item = LocationOut.model_validate(loc)
    item.display_path = loc.display_path
    return item


@router.put("/locations/{location_id}", response_model=LocationOut)
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(require_admin)):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    previous = loc.display_path
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    log_audit(db, current_user.id, f"Admin edited location #{loc.id}", "location", loc.id,
              previous_value=previous, new_value=loc.display_path)
    item = LocationOut.model_validate(loc)
    item.display_path = loc.display_path
    return item


@router.delete("/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    log_audit(db, current_user.id, f"Admin deleted location #{location_id}", "location", location_id)
    return {"detail": "Deleted"}
