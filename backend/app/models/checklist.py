from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChecklistTemplate(Base):
    """A named, configurable checklist for a given asset type (e.g. 'Fire Extinguisher - Standard')."""
    __tablename__ = "inspection_checklists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    asset_type = Column(String(30), nullable=False, index=True)  # matches AssetType value
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("ChecklistTemplateItem", back_populates="template",
                          cascade="all, delete-orphan", order_by="ChecklistTemplateItem.sort_order")


class ChecklistTemplateItem(Base):
    __tablename__ = "checklist_template_items"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("inspection_checklists.id"), nullable=False)
    section = Column(String(100), nullable=True)  # e.g. "Cabinet", "Hose Reel", "Physical condition"
    label = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)

    template = relationship("ChecklistTemplate", back_populates="items")
