import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class InspectionResult(str, enum.Enum):
    PASS = "pass"
    PASS_WITH_OBSERVATION = "pass_with_observation"
    REQUIRES_MAINTENANCE = "requires_maintenance"
    FAILED = "failed"


class InspectionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    RETURNED = "returned"


class ItemResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    NA = "not_applicable"


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checklist_template_id = Column(Integer, ForeignKey("inspection_checklists.id"), nullable=True)

    inspected_at = Column(DateTime, default=datetime.utcnow, index=True)
    overall_result = Column(Enum(InspectionResult), nullable=False)
    status = Column(Enum(InspectionStatus), default=InspectionStatus.SUBMITTED, index=True)

    general_remarks = Column(Text, nullable=True)
    defect_description = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)

    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    next_inspection_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="inspections")
    inspector = relationship("User", back_populates="inspections", foreign_keys=[inspector_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])
    items = relationship("InspectionItem", back_populates="inspection", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="inspection")


class InspectionItem(Base):
    __tablename__ = "inspection_items"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    section = Column(String(100), nullable=True)
    label = Column(String(255), nullable=False)
    result = Column(Enum(ItemResult), nullable=False)
    remarks = Column(Text, nullable=True)

    inspection = relationship("Inspection", back_populates="items")


class InspectionAssignment(Base):
    """Supervisor-created assignment of inspections to an inspector."""
    __tablename__ = "inspection_assignments"

    id = Column(Integer, primary_key=True, index=True)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    asset_ids_csv = Column(Text, nullable=True)  # comma-separated asset_id strings, e.g. "FE-00001,FE-00002"
    due_date = Column(DateTime, nullable=True)
    status = Column(String(30), default="assigned")  # assigned/in_progress/completed/reviewed/approved
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspector = relationship("User", foreign_keys=[inspector_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    building = relationship("Building")
