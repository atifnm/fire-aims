from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.records import MaintenanceType, DefectSeverity, DefectStatus, NotificationType


class MaintenanceCreate(BaseModel):
    asset_id: int
    service_date: date
    service_type: MaintenanceType
    previous_condition: Optional[str] = None
    work_performed: Optional[str] = None
    agent_used: Optional[str] = None
    quantity: Optional[str] = None
    service_provider: Optional[str] = None
    technician: Optional[str] = None
    cost: Optional[float] = None
    next_service_date: Optional[date] = None
    remarks: Optional[str] = None


class MaintenanceOut(MaintenanceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recorded_by_id: Optional[int] = None
    created_at: datetime


class DefectCreate(BaseModel):
    asset_id: int
    description: str
    severity: DefectSeverity = DefectSeverity.MEDIUM
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    corrective_action: Optional[str] = None


class DefectUpdate(BaseModel):
    status: Optional[DefectStatus] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    corrective_action: Optional[str] = None
    severity: Optional[DefectSeverity] = None


class DefectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    inspection_id: Optional[int] = None
    description: str
    severity: DefectSeverity
    status: DefectStatus
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    corrective_action: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int] = None
    asset_id: Optional[int] = None
    type: NotificationType
    message: str
    is_read: int
    created_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime


class AppSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    value: str
    description: Optional[str] = None


class AppSettingUpdate(BaseModel):
    value: str
