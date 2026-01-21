"""
Database models for repair cost estimations.
Links to detection records and stores cost breakdown.
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base


class CostEstimation(Base):
    """
    Cost estimation for a detection record.
    Contains breakdown of repair costs.
    """
    __tablename__ = "cost_estimations"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_record_id = Column(Integer, ForeignKey("detection_records.id"), nullable=False, unique=True)
    
    # Cost components (in USD)
    parts_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    paint_cost = Column(Float, default=0.0)
    markup = Column(Float, default=0.0)
    total_cost = Column(Float, nullable=False)
    
    # Estimation metadata
    estimated_labor_hours = Column(Float)
    labor_rate = Column(Float)  # Rate per hour
    markup_percentage = Column(Float)
    
    # Itemized breakdown
    cost_breakdown = Column(JSON)  # Detailed per-damage costs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    detection_record = relationship("DetectionRecord", back_populates="estimation")
    
    def __repr__(self):
        return f"<CostEstimation(id={self.id}, total=${self.total_cost:.2f})>"