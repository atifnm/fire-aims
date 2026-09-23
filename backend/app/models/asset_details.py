from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExtinguisherDetail(Base):
    __tablename__ = "extinguisher_details"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    extinguisher_type = Column(String(50), nullable=False, default="ABC Dry Chemical")
    extinguishing_medium = Column(String(100), nullable=True)
    capacity = Column(String(30), nullable=True)  # e.g. "9kg", "6L"
    manufacture_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)

    asset = relationship("Asset", back_populates="extinguisher_detail")


class HoseCabinetDetail(Base):
    __tablename__ = "hose_cabinet_details"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    cabinet_material = Column(String(100), nullable=True)
    has_glass_panel = Column(String(10), default="yes")

    asset = relationship("Asset", back_populates="hose_cabinet_detail")


class HoseReelDetail(Base):
    __tablename__ = "hose_reel_details"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    hose_length_m = Column(Float, nullable=True)
    hose_diameter_mm = Column(Float, nullable=True)

    asset = relationship("Asset", back_populates="hose_reel_detail")


class BranchDetail(Base):
    __tablename__ = "branch_details"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    nozzle_type = Column(String(100), nullable=True)  # jet/spray, adjustable, etc.
    condition = Column(String(50), nullable=True)

    asset = relationship("Asset", back_populates="branch_detail")


class McpDetail(Base):
    __tablename__ = "mcp_details"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    connected_panel = Column(String(150), nullable=True)
    zone_address = Column(String(50), nullable=True)
    last_functional_test = Column(Date, nullable=True)
    next_test_date = Column(Date, nullable=True)

    asset = relationship("Asset", back_populates="mcp_detail")
