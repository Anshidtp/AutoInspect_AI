"""
Cost estimation service layer.
Handles cost calculation and database storage.
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
import json

from backend.database.db_detection import DetectionRecord
from backend.database.db_estimation import CostEstimation

from backend.core.cost_estimator import CostEstimator
from backend.schemas.estimate_schema import (
                                        CostEstimationResponse,
                                        EstimationSummary,
                                        DamageCostItem
                                    )

logger = logging.getLogger(__name__)


class EstimationService:
    """
    Service layer for cost estimation operations.
    Coordinates cost calculation and database storage.
    """
    
    def __init__(self):
        self.estimator = CostEstimator()
    
    def create_estimation(
        self,
        detection_id: int,
        db: Session,
        labor_rate_override: Optional[float] = None,
        markup_override: Optional[float] = None,
        include_paint: bool = True
    ) -> CostEstimationResponse:
        """
        Create cost estimation for a detection record.
        
        Args:
            detection_id: ID of detection record
            db: Database session
            labor_rate_override: Override default labor rate
            markup_override: Override default markup percentage
            include_paint: Whether to include painting costs
            
        Returns:
            Cost estimation response
            
        Raises:
            HTTPException: If detection not found or estimation already exists
        """
        # Get detection record
        detection = db.query(DetectionRecord).filter(
            DetectionRecord.id == detection_id
        ).first()
        
        if not detection:
            raise HTTPException(status_code=404, detail="Detection record not found")
        
        # Check if estimation already exists
        existing = db.query(CostEstimation).filter(
            CostEstimation.detection_record_id == detection_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Cost estimation already exists for this detection. Use update endpoint."
            )
        
        # Prepare damages data
        damages = [
            {
                "damage_type": d.damage_type,
                "severity": d.severity or "moderate",
                "confidence": d.confidence
            }
            for d in detection.damages
        ]
        
        if not damages:
            raise HTTPException(
                status_code=400,
                detail="No damages detected. Cannot create estimation."
            )
        
        # Calculate costs
        estimation_data = self.estimator.estimate_total_cost(
            damages,
            include_paint=include_paint,
            labor_rate_override=labor_rate_override,
            markup_override=markup_override
        )
        
        # Create estimation record
        estimation = CostEstimation(
            detection_record_id=detection_id,
            parts_cost=estimation_data["parts_cost"],
            labor_cost=estimation_data["labor_cost"],
            paint_cost=estimation_data["paint_cost"],
            markup=estimation_data["markup"],
            total_cost=estimation_data["total_cost"],
            estimated_labor_hours=estimation_data["estimated_labor_hours"],
            labor_rate=estimation_data["labor_rate"],
            markup_percentage=estimation_data["markup_percentage"],
            cost_breakdown={"items": estimation_data["damage_items"]}
        )
        
        db.add(estimation)
        db.commit()
        db.refresh(estimation)
        
        # Prepare response
        response = CostEstimationResponse(
            estimation_id=estimation.id,
            detection_id=detection_id,
            parts_cost=estimation.parts_cost,
            labor_cost=estimation.labor_cost,
            paint_cost=estimation.paint_cost,
            markup=estimation.markup,
            total_cost=estimation.total_cost,
            estimated_labor_hours=estimation.estimated_labor_hours,
            labor_rate=estimation.labor_rate,
            markup_percentage=estimation.markup_percentage,
            damage_items=[DamageCostItem(**item) for item in estimation_data["damage_items"]],
            created_at=estimation.created_at
        )
        
        logger.info(f"Created cost estimation for detection {detection_id}: ${estimation.total_cost:.2f}")
        return response
    
    def get_estimation_by_detection_id(
        self,
        detection_id: int,
        db: Session
    ) -> Optional[CostEstimationResponse]:
        """
        Retrieve cost estimation for a detection.
        
        Args:
            detection_id: ID of detection record
            db: Database session
            
        Returns:
            Cost estimation or None
        """
        estimation = db.query(CostEstimation).filter(
            CostEstimation.detection_record_id == detection_id
        ).first()
        
        if not estimation:
            return None
        
        # Parse damage items from breakdown
        damage_items = []
        if estimation.cost_breakdown and "items" in estimation.cost_breakdown:
            damage_items = [DamageCostItem(**item) for item in estimation.cost_breakdown["items"]]
        
        return CostEstimationResponse(
            estimation_id=estimation.id,
            detection_id=estimation.detection_record_id,
            parts_cost=estimation.parts_cost,
            labor_cost=estimation.labor_cost,
            paint_cost=estimation.paint_cost,
            markup=estimation.markup,
            total_cost=estimation.total_cost,
            estimated_labor_hours=estimation.estimated_labor_hours,
            labor_rate=estimation.labor_rate,
            markup_percentage=estimation.markup_percentage,
            damage_items=damage_items,
            created_at=estimation.created_at
        )
    
    def get_estimation_summary(
        self,
        detection_id: int,
        db: Session
    ) -> Optional[EstimationSummary]:
        """
        Get summary of cost estimation.
        
        Args:
            detection_id: ID of detection record
            db: Database session
            
        Returns:
            Estimation summary or None
        """
        detection = db.query(DetectionRecord).filter(
            DetectionRecord.id == detection_id
        ).first()
        
        if not detection:
            return None
        
        estimation = db.query(CostEstimation).filter(
            CostEstimation.detection_record_id == detection_id
        ).first()
        
        # Get severity breakdown
        damages = [
            {"severity": d.severity or "moderate"}
            for d in detection.damages
        ]
        severity_breakdown = self.estimator.get_severity_breakdown(damages)
        
        # Estimate repair time
        labor_hours = estimation.estimated_labor_hours if estimation else 0
        repair_time = self.estimator.estimate_repair_time(labor_hours)
        
        return EstimationSummary(
            detection_id=detection_id,
            total_damages=len(detection.damages),
            total_cost=estimation.total_cost if estimation else 0.0,
            estimated_repair_time=repair_time,
            severity_breakdown=severity_breakdown
        )
    
    def update_estimation(
        self,
        detection_id: int,
        db: Session,
        labor_rate_override: Optional[float] = None,
        markup_override: Optional[float] = None,
        include_paint: bool = True
    ) -> CostEstimationResponse:
        """
        Update existing cost estimation.
        
        Args:
            detection_id: ID of detection record
            db: Database session
            labor_rate_override: New labor rate
            markup_override: New markup percentage
            include_paint: Whether to include painting costs
            
        Returns:
            Updated cost estimation
            
        Raises:
            HTTPException: If estimation not found
        """
        estimation = db.query(CostEstimation).filter(
            CostEstimation.detection_record_id == detection_id
        ).first()
        
        if not estimation:
            raise HTTPException(status_code=404, detail="Cost estimation not found")
        
        # Get detection and damages
        detection = estimation.detection_record
        damages = [
            {
                "damage_type": d.damage_type,
                "severity": d.severity or "moderate",
                "confidence": d.confidence
            }
            for d in detection.damages
        ]
        
        # Recalculate costs
        estimation_data = self.estimator.estimate_total_cost(
            damages,
            include_paint=include_paint,
            labor_rate_override=labor_rate_override,
            markup_override=markup_override
        )
        
        # Update estimation
        estimation.parts_cost = estimation_data["parts_cost"]
        estimation.labor_cost = estimation_data["labor_cost"]
        estimation.paint_cost = estimation_data["paint_cost"]
        estimation.markup = estimation_data["markup"]
        estimation.total_cost = estimation_data["total_cost"]
        estimation.estimated_labor_hours = estimation_data["estimated_labor_hours"]
        estimation.labor_rate = estimation_data["labor_rate"]
        estimation.markup_percentage = estimation_data["markup_percentage"]
        estimation.cost_breakdown = {"items": estimation_data["damage_items"]}
        
        db.commit()
        db.refresh(estimation)
        
        response = CostEstimationResponse(
            estimation_id=estimation.id,
            detection_id=detection_id,
            parts_cost=estimation.parts_cost,
            labor_cost=estimation.labor_cost,
            paint_cost=estimation.paint_cost,
            markup=estimation.markup,
            total_cost=estimation.total_cost,
            estimated_labor_hours=estimation.estimated_labor_hours,
            labor_rate=estimation.labor_rate,
            markup_percentage=estimation.markup_percentage,
            damage_items=[DamageCostItem(**item) for item in estimation_data["damage_items"]],
            created_at=estimation.created_at
        )
        
        logger.info(f"Updated cost estimation for detection {detection_id}")
        return response