from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class BuildingBase(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BuildingOut(BuildingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class FloorBase(BaseModel):
    building_id: int
    name: str
    floor_plan_reference: Optional[str] = None


class FloorCreate(FloorBase):
    pass


class FloorUpdate(BaseModel):
    building_id: Optional[int] = None
    name: Optional[str] = None
    floor_plan_reference: Optional[str] = None


class FloorOut(FloorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LocationBase(BaseModel):
    floor_id: int
    department: Optional[str] = None
    room: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    floor_id: Optional[int] = None
    department: Optional[str] = None
    room: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationOut(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    display_path: Optional[str] = None
