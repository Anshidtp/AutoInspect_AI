from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any
from datetime import datetime


class DamageCostItem(BaseModel):
    """Individual damage cost breakdown."""
    damage_type: str
    severity: str
    parts_cost: float = Field(ge=0.0)
    labor_hours: float = Field(ge=0.0)
    labor_cost: float = Field(ge=0.0)
    paint_cost: float = Field(ge=0.0, default=0.0)
    subtotal: float = Field(ge=0.0)


class CostEstimationRequest(BaseModel):
    """Request schema for cost estimation."""
    detection_id: int = Field(..., description="ID of the detection record")
    labor_rate_override: Optional[float] = Field(None, ge=0.0, description="Override default labor rate")
    markup_override: Optional[float] = Field(None, ge=0.0, le=100.0, description="Override markup percentage")
    include_paint: Optional[bool] = Field(True, description="Include painting costs")


class CostEstimationResponse(BaseModel):
    """Response schema for cost estimation."""
    estimation_id: int
    detection_id: int

    # Summary costs
    parts_cost: float
    labor_cost: float
    paint_cost: float
    markup: float
    total_cost: float

    # Metadata
    estimated_labor_hours: float
    labor_rate: float
    markup_percentage: float

    # Detailed breakdown
    damage_items: List[DamageCostItem]

    # Timestamps
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CostEstimationInDB(BaseModel):
    """Schema for cost estimation from database."""
    id: int
    detection_record_id: int
    parts_cost: float
    labor_cost: float
    paint_cost: float
    markup: float
    total_cost: float
    estimated_labor_hours: Optional[float]
    labor_rate: Optional[float]
    
    """Individual damage cost breakdown."""
    damage_type: str
    severity: str
    parts_cost: float = Field(ge=0.0)
    labor_hours: float = Field(ge=0.0)
    labor_cost: float = Field(ge=0.0)
    paint_cost: float = Field(ge=0.0, default=0.0)
    subtotal: float = Field(ge=0.0)


class CostEstimationRequest(BaseModel):
    """Request schema for cost estimation."""
    detection_id: int = Field(..., description="ID of the detection record")
    labor_rate_override: Optional[float] = Field(None, ge=0.0, description="Override default labor rate")
    markup_override: Optional[float] = Field(None, ge=0.0, le=100.0, description="Override markup percentage")
    include_paint: Optional[bool] = Field(True, description="Include painting costs")


class CostEstimationResponse(BaseModel):
    """Response schema for cost estimation."""
    estimation_id: int
    detection_id: int
    
    # Summary costs
    parts_cost: float
    labor_cost: float
    paint_cost: float
    markup: float
    total_cost: float
    
    # Metadata
    estimated_labor_hours: float
    labor_rate: float
    markup_percentage: float
    
    # Detailed breakdown
    damage_items: List[DamageCostItem]
    
    # Timestamps
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CostEstimationInDB(BaseModel):
    """Schema for cost estimation from database."""
    id: int
    detection_record_id: int
    parts_cost: float
    labor_cost: float
    paint_cost: float
    markup: float
    total_cost: float
    estimated_labor_hours: Optional[float]
    labor_rate: Optional[float]
    markup_percentage: Optional[float]
    cost_breakdown: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EstimationSummary(BaseModel):
    """Summary schema for quick cost overview."""
    detection_id: int
    total_damages: int
    total_cost: float
    estimated_repair_time: str  # e.g., "2-3 days"
    severity_breakdown: Dict[str, int]  # {"minor": 2, "moderate": 1}