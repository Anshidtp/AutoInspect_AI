from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database.db import get_db
from backend.schemas.response_schema import DetectionResponse, DetectionRecordInDB, DetectionListResponse
from backend.services.detection_service import DetectionService
from backend.database.db_detection import DetectionRecord

router = APIRouter(prefix="/detections", tags=["Detection"])


@router.post("/", response_model=DetectionResponse, status_code=201)
async def detect_damage(
    file: UploadFile = File(..., description="Image file to analyze"),
    confidence_threshold: Optional[float] = Form(None, ge=0.0, le=1.0),
    detect_severity: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload an image and detect car damages.
    
    **Parameters:**
    - **file**: Image file (JPG, JPEG, or PNG)
    - **confidence_threshold**: Minimum confidence for detections (0.0-1.0)
    - **detect_severity**: Whether to classify damage severity
    
    **Returns:**
    - Detection results with bounding boxes and damage classifications
    """
    service = DetectionService()
    return await service.detect_damages(
        upload_file=file,
        db=db,
        confidence_threshold=confidence_threshold,
        detect_severity=detect_severity
    )


@router.get("/{detection_id}", response_model=DetectionRecordInDB)
def get_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific detection record by ID.
    
    **Parameters:**
    - **detection_id**: ID of the detection record
    
    **Returns:**
    - Complete detection record with all detected damages
    """
    service = DetectionService()
    record = service.get_detection_by_id(detection_id, db)
    
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found")
    
    return record


@router.get("/", response_model=DetectionListResponse)
def list_detections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all detection records with pagination.
    
    **Parameters:**
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    
    **Returns:**
    - Paginated list of detection records
    """
    service = DetectionService()
    skip = (page - 1) * page_size
    
    records = service.list_detections(db, skip=skip, limit=page_size)
    
    # Get total count
    
    total = db.query(DetectionRecord).count()
    
    return DetectionListResponse(
        total=total,
        records=records,
        page=page,
        page_size=page_size
    )


@router.delete("/{detection_id}", status_code=204)
def delete_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a detection record and associated data.
    
    **Parameters:**
    - **detection_id**: ID of the detection to delete
    
    **Returns:**
    - 204 No Content on success
    """
    service = DetectionService()
    deleted = service.delete_detection(detection_id, db)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Detection record not found")
    
    return None