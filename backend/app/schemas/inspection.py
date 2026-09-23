from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.inspection import InspectionResult, InspectionStatus, ItemResult


class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    section: Optional[str] = None
    label: str
    sort_order: int
    is_required: bool


class ChecklistItemCreate(BaseModel):
    section: Optional[str] = None
    label: str
    sort_order: int = 0
    is_required: bool = True


class ChecklistTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    asset_type: str
    is_active: bool
    items: List[ChecklistItemOut] = []


class ChecklistTemplateCreate(BaseModel):
    name: str
    asset_type: str
    items: List[ChecklistItemCreate] = []


class InspectionItemIn(BaseModel):
    section: Optional[str] = None
    label: str
    result: ItemResult
    remarks: Optional[str] = None


class InspectionItemOut(InspectionItemIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class InspectionCreate(BaseModel):
    asset_id: int
    checklist_template_id: Optional[int] = None
    overall_result: InspectionResult
    general_remarks: Optional[str] = None
    defect_description: Optional[str] = None
    corrective_action: Optional[str] = None
    defect_severity: Optional[str] = None  # low/medium/high/critical - creates a Defect if provided
    items: List[InspectionItemIn] = []


class InspectionReview(BaseModel):
    approve: bool
    review_notes: Optional[str] = None


class InspectionAdminUpdate(BaseModel):
    """Admin-only correction of an already-submitted inspection record. Every change is audit-logged."""
    overall_result: Optional[InspectionResult] = None
    general_remarks: Optional[str] = None
    defect_description: Optional[str] = None
    corrective_action: Optional[str] = None
    next_inspection_date: Optional[datetime] = None
    correction_reason: str


class InspectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    inspector_id: int
    inspected_at: datetime
    overall_result: InspectionResult
    status: InspectionStatus
    general_remarks: Optional[str] = None
    defect_description: Optional[str] = None
    corrective_action: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    next_inspection_date: Optional[datetime] = None
    items: List[InspectionItemOut] = []


class InspectionAssignmentCreate(BaseModel):
    inspector_id: int
    building_id: Optional[int] = None
    asset_ids: List[str] = []  # list of human asset_id strings e.g. ["FE-00001","FE-00002"]
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InspectionAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    inspector_id: int
    assigned_by_id: int
    building_id: Optional[int] = None
    asset_ids_csv: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
