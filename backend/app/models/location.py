from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(30), unique=True, index=True, nullable=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")


class Floor(Base):
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g. "Ground Floor", "Floor 2"
    floor_plan_reference = Column(String(255), nullable=True)  # future map feature
    created_at = Column(DateTime, default=datetime.utcnow)

    building = relationship("Building", back_populates="floors")
    locations = relationship("Location", back_populates="floor", cascade="all, delete-orphan")


class Location(Base):
    """A specific point/area within a floor - room, corridor, department, etc."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)
    department = Column(String(100), nullable=True)
    room = Column(String(100), nullable=True)
    area = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)  # "Near Emergency Exit"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    floor = relationship("Floor", back_populates="locations")
    assets = relationship("Asset", back_populates="location")

    @property
    def display_path(self):
        parts = [self.floor.building.name if self.floor and self.floor.building else None,
                 self.floor.name if self.floor else None,
                 self.department, self.room, self.area]
        return " → ".join([p for p in parts if p])
