from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.asset import AssetType, AssetStatus


class ExtinguisherDetailSchema(BaseModel):
    extinguisher_type: str = "ABC Dry Chemical"
    extinguishing_medium: Optional[str] = None
    capacity: Optional[str] = None
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class HoseCabinetDetailSchema(BaseModel):
    cabinet_material: Optional[str] = None
    has_glass_panel: Optional[str] = "yes"

    model_config = ConfigDict(from_attributes=True)


class HoseReelDetailSchema(BaseModel):
    hose_length_m: Optional[float] = None
    hose_diameter_mm: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class BranchDetailSchema(BaseModel):
    nozzle_type: Optional[str] = None
    condition: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class McpDetailSchema(BaseModel):
    connected_panel: Optional[str] = None
    zone_address: Optional[str] = None
    last_functional_test: Optional[date] = None
    next_test_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class AssetBase(BaseModel):
    asset_type: AssetType
    location_id: Optional[int] = None
    specific_location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    assigned_department: Optional[str] = None
    remarks: Optional[str] = None
    parent_asset_id: Optional[int] = None


class AssetCreate(AssetBase):
    extinguisher_detail: Optional[ExtinguisherDetailSchema] = None
    hose_cabinet_detail: Optional[HoseCabinetDetailSchema] = None
    hose_reel_detail: Optional[HoseReelDetailSchema] = None
    branch_detail: Optional[BranchDetailSchema] = None
    mcp_detail: Optional[McpDetailSchema] = None


class AssetUpdate(BaseModel):
    location_id: Optional[int] = None
    specific_location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    assigned_department: Optional[str] = None
    remarks: Optional[str] = None
    status: Optional[AssetStatus] = None
    extinguisher_detail: Optional[ExtinguisherDetailSchema] = None
    hose_cabinet_detail: Optional[HoseCabinetDetailSchema] = None
    hose_reel_detail: Optional[HoseReelDetailSchema] = None
    branch_detail: Optional[BranchDetailSchema] = None
    mcp_detail: Optional[McpDetailSchema] = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: str
    asset_type: AssetType
    status: AssetStatus
    location_id: Optional[int] = None
    location_path: Optional[str] = None
    specific_location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[date] = None
    last_inspection_date: Optional[datetime] = None
    next_inspection_date: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_date: Optional[datetime] = None
    assigned_department: Optional[str] = None
    remarks: Optional[str] = None
    qr_code_path: Optional[str] = None
    barcode_path: Optional[str] = None
    parent_asset_id: Optional[int] = None
    created_at: datetime

    extinguisher_detail: Optional[ExtinguisherDetailSchema] = None
    hose_cabinet_detail: Optional[HoseCabinetDetailSchema] = None
    hose_reel_detail: Optional[HoseReelDetailSchema] = None
    branch_detail: Optional[BranchDetailSchema] = None
    mcp_detail: Optional[McpDetailSchema] = None
