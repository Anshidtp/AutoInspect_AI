from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class DamageBase(BaseModel):
    """Base schema for detected damage."""
    damage_type: str = Field(..., description="Type of damage detected")
    severity: Optional[str] = Field(None, description="Severity level: minor, moderate, severe")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    affected_part: Optional[str] = Field(None, description="Car part affected by damage")


class DamageDetection(DamageBase):
    """Schema for individual damage detection with bounding box."""
    bbox_x: float = Field(..., ge=0.0, le=1.0, description="Normalized x-coordinate")
    bbox_y: float = Field(..., ge=0.0, le=1.0, description="Normalized y-coordinate")
    bbox_width: float = Field(..., ge=0.0, le=1.0, description="Normalized width")
    bbox_height: float = Field(..., ge=0.0, le=1.0, description="Normalized height")
    additional_info: Optional[Dict[str, Any]] = None


class DamageInDB(DamageDetection):
    """Schema for damage stored in database."""
    id: int
    detection_record_id: int
    
    model_config = ConfigDict(from_attributes=True)


class DetectionRequest(BaseModel):
    """Request schema for damage detection (multipart form)."""
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    detect_severity: Optional[bool] = Field(True, description="Classify severity levels")


class DetectionResponse(BaseModel):
    """Response schema for damage detection results."""
    detection_id: int
    image_filename: str
    image_dimensions: Dict[str, int]  # {"width": 1920, "height": 1080}
    damages_detected: List[DamageDetection]
    total_damages: int
    processing_time: float
    model_version: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DetectionRecordBase(BaseModel):
    """Base schema for detection record."""
    original_filename: str
    file_size: int
    image_width: int
    image_height: int


class DetectionRecordInDB(DetectionRecordBase):
    """Schema for detection record from database."""
    id: int
    image_path: str
    model_version: str
    confidence_threshold: float
    created_at: datetime
    processing_time: Optional[float]
    damages: List[DamageInDB] = []
    
    model_config = ConfigDict(from_attributes=True)


class DetectionListResponse(BaseModel):
    """Response schema for listing detection records."""
    total: int
    records: List[DetectionRecordInDB]
    page: int
    page_size: int