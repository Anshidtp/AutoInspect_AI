from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base


class DetectionRecord(Base):
    """
    Main detection record storing uploaded image information.
    One record per image upload/detection request.
    """
    __tablename__ = "detection_records"
    
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes
    image_width = Column(Integer)
    image_height = Column(Integer)
    model_version = Column(String, default="yolov8n")
    confidence_threshold = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds
    
    # Relationships
    damages = relationship("DetectedDamage", back_populates="detection_record", cascade="all, delete-orphan")
    estimation = relationship("CostEstimation", back_populates="detection_record", uselist=False)
    
    def __repr__(self):
        return f"<DetectionRecord(id={self.id}, filename={self.original_filename})>"


class DetectedDamage(Base):
    """
    Individual damage detected in an image.
    Multiple damages can be detected in a single image.
    """
    __tablename__ = "detected_damages"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_record_id = Column(Integer, ForeignKey("detection_records.id"), nullable=False)
    
    # Damage classification
    damage_type = Column(String, nullable=False)  # e.g., "dent", "scratch", "broken_light"
    severity = Column(String)  # e.g., "minor", "moderate", "severe"
    confidence = Column(Float, nullable=False)  # YOLO confidence score
    
    # Bounding box coordinates (normalized 0-1)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    
    # Additional metadata
    affected_part = Column(String)  # e.g., "front_bumper", "door", "hood"
    additional_info = Column(JSON)  # Any extra detection metadata
    
    # Relationships
    detection_record = relationship("DetectionRecord", back_populates="damages")
    
    def __repr__(self):
        return f"<DetectedDamage(id={self.id}, type={self.damage_type}, confidence={self.confidence})>"