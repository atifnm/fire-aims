import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class AssetType(str, enum.Enum):
    EXTINGUISHER = "extinguisher"
    HOSE_CABINET = "hose_cabinet"
    HOSE_REEL = "hose_reel"
    BRANCH = "branch"
    MCP = "mcp"


class AssetStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    DUE_SOON = "due_soon"
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"
    DEFECTIVE = "defective"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_SERVICE = "out_of_service"


ASSET_PREFIX = {
    AssetType.EXTINGUISHER: "FE",
    AssetType.HOSE_CABINET: "HC",
    AssetType.HOSE_REEL: "HR",
    AssetType.BRANCH: "BR",
    AssetType.MCP: "MCP",
}


class Asset(Base):
    """
    Generic asset record. Every physical piece of fire safety equipment
    (extinguisher, hose cabinet, hose reel, branch/nozzle, MCP) gets one row
    here holding the fields common to all equipment, plus a 1:1 link to a
    type-specific detail table for fields unique to that equipment type.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(20), unique=True, index=True, nullable=False)  # FE-00001
    asset_type = Column(Enum(AssetType), nullable=False, index=True)

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    specific_location = Column(String(255), nullable=True)  # free-text override e.g. "Near Main Entrance"

    manufacturer = Column(String(150), nullable=True)
    model = Column(String(150), nullable=True)
    serial_number = Column(String(150), nullable=True, index=True)

    installation_date = Column(Date, nullable=True)

    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.COMPLIANT, index=True)

    last_inspection_date = Column(DateTime, nullable=True)
    next_inspection_date = Column(DateTime, nullable=True, index=True)

    last_service_date = Column(DateTime, nullable=True)
    next_service_date = Column(DateTime, nullable=True, index=True)

    assigned_department = Column(String(150), nullable=True)
    remarks = Column(Text, nullable=True)

    qr_code_path = Column(String(255), nullable=True)
    barcode_path = Column(String(255), nullable=True)

    # Optional: a hose cabinet component may belong to a parent cabinet asset
    parent_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = relationship("Location", back_populates="assets")
    parent_asset = relationship("Asset", remote_side=[id], backref="components")

    extinguisher_detail = relationship("ExtinguisherDetail", back_populates="asset", uselist=False,
                                        cascade="all, delete-orphan")
    hose_cabinet_detail = relationship("HoseCabinetDetail", back_populates="asset", uselist=False,
                                        cascade="all, delete-orphan")
    hose_reel_detail = relationship("HoseReelDetail", back_populates="asset", uselist=False,
                                     cascade="all, delete-orphan")
    branch_detail = relationship("BranchDetail", back_populates="asset", uselist=False,
                                  cascade="all, delete-orphan")
    mcp_detail = relationship("McpDetail", back_populates="asset", uselist=False,
                               cascade="all, delete-orphan")

    inspections = relationship("Inspection", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset", cascade="all, delete-orphan")
    defects = relationship("Defect", back_populates="asset", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="asset", cascade="all, delete-orphan")

    @property
    def location_path(self):
        base = self.location.display_path if self.location else ""
        if self.specific_location:
            return f"{base} → {self.specific_location}" if base else self.specific_location
        return base
