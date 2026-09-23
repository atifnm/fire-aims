import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Date
from sqlalchemy.orm import relationship
from app.core.database import Base


class MaintenanceType(str, enum.Enum):
    REFILLED = "refilled"
    SERVICED = "serviced"
    REPAIRED = "repaired"
    REPLACED = "replaced"
    OTHER = "other"


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)

    service_date = Column(Date, nullable=False, default=datetime.utcnow)
    service_type = Column(Enum(MaintenanceType), nullable=False)
    previous_condition = Column(Text, nullable=True)
    work_performed = Column(Text, nullable=True)
    agent_used = Column(String(150), nullable=True)
    quantity = Column(String(50), nullable=True)
    service_provider = Column(String(150), nullable=True)
    technician = Column(String(150), nullable=True)
    cost = Column(Float, nullable=True)
    next_service_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)

    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="maintenance_records")
    recorded_by = relationship("User")
    photos = relationship("Photo", back_populates="maintenance_record")


class DefectSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DefectStatus(str, enum.Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"


class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)

    description = Column(Text, nullable=False)
    severity = Column(Enum(DefectSeverity), default=DefectSeverity.MEDIUM, index=True)
    status = Column(Enum(DefectStatus), default=DefectStatus.OPEN, index=True)
    assigned_to = Column(String(150), nullable=True)
    due_date = Column(Date, nullable=True)
    corrective_action = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="defects")
    inspection = relationship("Inspection")


class PhotoContext(str, enum.Enum):
    GENERAL = "general"
    BEFORE_INSPECTION = "before_inspection"
    DEFECT = "defect"
    AFTER_MAINTENANCE = "after_maintenance"


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    maintenance_record_id = Column(Integer, ForeignKey("maintenance_records.id"), nullable=True)

    file_path = Column(String(500), nullable=False)
    context = Column(Enum(PhotoContext), default=PhotoContext.GENERAL)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="photos")
    inspection = relationship("Inspection", back_populates="photos")
    maintenance_record = relationship("MaintenanceRecord", back_populates="photos")
    uploaded_by = relationship("User")


class NotificationType(str, enum.Enum):
    DUE_SOON = "due_soon"
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"
    DEFECT = "defect"
    ASSIGNMENT = "assignment"
    APPROVAL = "approval"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null = broadcast to admins/supervisors
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    asset = relationship("Asset")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")


class AppSetting(Base):
    """Key-value store for configurable business rules (thresholds, intervals, etc.)."""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
