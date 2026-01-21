from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.db import get_db
from backend.schemas.estimate_schema import (
    CostEstimationRequest,
    CostEstimationResponse,
    EstimationSummary
)
from backend.services.estimation_service import EstimationService

router = APIRouter(prefix="/estimations", tags=["Cost Estimation"])


@router.post("/", response_model=CostEstimationResponse, status_code=201)
def create_cost_estimation(
    detection_id: int = Body(..., description="Detection record ID"),
    labor_rate_override: Optional[float] = Body(None, ge=0.0, description="Custom labor rate per hour"),
    markup_override: Optional[float] = Body(None, ge=0.0, le=100.0, description="Custom markup percentage"),
    include_paint: bool = Body(True, description="Include painting costs"),
    db: Session = Depends(get_db)
):
    """
    Create a cost estimation for detected damages.
    
    **Parameters:**
    - **detection_id**: ID of the detection record
    - **labor_rate_override**: Optional custom labor rate (USD/hour)
    - **markup_override**: Optional custom markup percentage
    - **include_paint**: Whether to include painting costs
    
    **Returns:**
    - Complete cost breakdown with itemized damages
    """
    service = EstimationService()
    return service.create_estimation(
        detection_id=detection_id,
        db=db,
        labor_rate_override=labor_rate_override,
        markup_override=markup_override,
        include_paint=include_paint
    )


@router.get("/detection/{detection_id}", response_model=CostEstimationResponse)
def get_estimation_by_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Get cost estimation for a detection record.
    
    **Parameters:**
    - **detection_id**: ID of the detection record
    
    **Returns:**
    - Cost estimation if it exists
    """
    service = EstimationService()
    estimation = service.get_estimation_by_detection_id(detection_id, db)
    
    if not estimation:
        raise HTTPException(
            status_code=404,
            detail="Cost estimation not found for this detection"
        )
    
    return estimation


@router.get("/summary/{detection_id}", response_model=EstimationSummary)
def get_estimation_summary(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a summary of cost estimation.
    
    **Parameters:**
    - **detection_id**: ID of the detection record
    
    **Returns:**
    - Quick overview with total cost and repair time
    """
    service = EstimationService()
    summary = service.get_estimation_summary(detection_id, db)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    return summary


@router.put("/{detection_id}", response_model=CostEstimationResponse)
def update_cost_estimation(
    detection_id: int,
    labor_rate_override: Optional[float] = Body(None, ge=0.0),
    markup_override: Optional[float] = Body(None, ge=0.0, le=100.0),
    include_paint: bool = Body(True),
    db: Session = Depends(get_db)
):
    """
    Update an existing cost estimation.
    
    **Parameters:**
    - **detection_id**: ID of the detection record
    - **labor_rate_override**: New labor rate
    - **markup_override**: New markup percentage
    - **include_paint**: Whether to include painting costs
    
    **Returns:**
    - Updated cost estimation
    """
    service = EstimationService()
    return service.update_estimation(
        detection_id=detection_id,
        db=db,
        labor_rate_override=labor_rate_override,
        markup_override=markup_override,
        include_paint=include_paint
    )