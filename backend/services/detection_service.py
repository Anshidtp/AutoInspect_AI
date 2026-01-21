import time
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
import logging

from backend.database.db_detection import DetectionRecord, DetectedDamage
from backend.schemas.response_schema import DetectionResponse, DetectionRecordInDB

from backend.core.damage_detector import DamageDetector
from backend.core.image_processor import ImageProcessor
from backend.utils.file_handler import FileHandler


logger = logging.getLogger(__name__)


class DetectionService:
    """
    Service layer for damage detection operations.
    Coordinates file handling, ML inference, and database storage.
    """
    
    def __init__(self):
        self.detector = DamageDetector()
        self.image_processor = ImageProcessor()
        self.file_handler = FileHandler()
    
    async def detect_damages(
        self,
        upload_file: UploadFile,
        db: Session,
        confidence_threshold: Optional[float] = None,
        detect_severity: bool = True
    ) -> DetectionResponse:
        """
        Detect damages in uploaded image.
        
        Args:
            upload_file: Uploaded image file
            db: Database session
            confidence_threshold: Detection confidence threshold
            detect_severity: Whether to classify severity
            
        Returns:
            DetectionResponse with results
        """
        start_time = time.time()
        
        # Save uploaded file
        file_path, file_size = await self.file_handler.save_upload_file(upload_file)
        
        try:
            # Load and process image
            image = self.image_processor.load_image(file_path)
            width, height = self.image_processor.get_image_dimensions(image)
            
            # Run detection
            damages = self.detector.detect(
                image,
                confidence_threshold=confidence_threshold
            )
            
            processing_time = time.time() - start_time
            
            # Create detection record in database
            detection_record = DetectionRecord(
                image_path=file_path,
                original_filename=upload_file.filename,
                file_size=file_size,
                image_width=width,
                image_height=height,
                model_version=self.detector.get_model_info()["model_type"],
                confidence_threshold=confidence_threshold or self.detector.confidence_threshold,
                processing_time=processing_time
            )
            
            db.add(detection_record)
            db.flush()  # Get the ID
            
            # Save detected damages
            for damage in damages:
                detected_damage = DetectedDamage(
                    detection_record_id=detection_record.id,
                    damage_type=damage["damage_type"],
                    severity=damage.get("severity", "moderate"),
                    confidence=damage["confidence"],
                    bbox_x=damage["bbox_x"],
                    bbox_y=damage["bbox_y"],
                    bbox_width=damage["bbox_width"],
                    bbox_height=damage["bbox_height"],
                    affected_part=damage.get("affected_part"),
                    additional_info={"class_id": damage.get("class_id")}
                )
                db.add(detected_damage)
            
            db.commit()
            db.refresh(detection_record)
            
            # Prepare response
            response = DetectionResponse(
                detection_id=detection_record.id,
                image_filename=upload_file.filename,
                image_dimensions={"width": width, "height": height},
                damages_detected=damages,
                total_damages=len(damages),
                processing_time=processing_time,
                model_version=detection_record.model_version,
                timestamp=detection_record.created_at
            )
            
            logger.info(f"Detection complete: {len(damages)} damages found in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            db.rollback()
            # Clean up uploaded file on error
            self.file_handler.delete_file(file_path)
            logger.error(f"Detection failed: {e}")
            raise
    
    def get_detection_by_id(self, detection_id: int, db: Session) -> Optional[DetectionRecordInDB]:
        """
        Retrieve detection record by ID.
        
        Args:
            detection_id: ID of detection record
            db: Database session
            
        Returns:
            Detection record or None
        """
        record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
        if record:
            return DetectionRecordInDB.model_validate(record)
        return None
    
    def list_detections(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10
    ) -> List[DetectionRecordInDB]:
        """
        List detection records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of detection records
        """
        records = db.query(DetectionRecord).order_by(
            DetectionRecord.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [DetectionRecordInDB.model_validate(r) for r in records]
    
    def delete_detection(self, detection_id: int, db: Session) -> bool:
        """
        Delete detection record and associated file.
        
        Args:
            detection_id: ID of detection to delete
            db: Database session
            
        Returns:
            True if deleted successfully
        """
        record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
        if not record:
            return False
        
        # Delete file
        self.file_handler.delete_file(record.image_path)
        
        # Delete from database (cascades to damages and estimation)
        db.delete(record)
        db.commit()
        
        logger.info(f"Deleted detection record {detection_id}")
        return True