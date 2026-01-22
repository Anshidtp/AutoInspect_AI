from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging
from backend.config.settings import settings
from backend.core.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class DamageDetector:
    """
    Car damage detector using YOLOv8.
    Detects 11 types of car damage and classifies severity.
    """
    
    # Damage type mappings (matches your trained model classes)
    DAMAGE_CLASSES = {
        0: "damaged_head_light",
        1: "damaged_hood",
        2: "damaged_trunk",
        3: "damaged_window",
        4: "damaged_windscreen",
        5: "damaged_bumper",
        6: "damaged_door",
        7: "damaged_fender",
        8: "damaged_mirror_glass",
        9: "dent_or_scratch",
        10: "missing_grille"
    }
    
    # Reverse mapping for easy lookup
    CLASS_TO_ID = {v: k for k, v in DAMAGE_CLASSES.items()}
    
    # Car part mappings (derived from damage type)
    PART_MAPPING = {
        "damaged_head_light": "headlight",
        "damaged_hood": "hood",
        "damaged_trunk": "trunk",
        "damaged_window": "window",
        "damaged_windscreen": "windscreen",
        "damaged_bumper": "bumper",
        "damaged_door": "door",
        "damaged_fender": "fender",
        "damaged_mirror_glass": "mirror",
        "dent_or_scratch": None,  # Will infer from position
        "missing_grille": "grille"
    }
    
    # Severity rules based on damage type
    SEVERITY_RULES = {
        "damaged_windscreen": "severe",      # Safety critical
        "damaged_window": "moderate",
        "damaged_head_light": "moderate",    # Affects visibility
        "missing_grille": "minor",
        "damaged_mirror_glass": "moderate",
        "damaged_hood": "moderate",
        "damaged_trunk": "moderate",
        "damaged_door": "moderate",
        "damaged_fender": "moderate",
        "damaged_bumper": "moderate",
        "dent_or_scratch": None  # Will determine from size
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize damage detector with YOLO model.
        
        Args:
            model_path: Path to trained YOLO model weights
        """
        self.model_path = model_path or settings.MODEL_PATH
        self.confidence_threshold = settings.MODEL_CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.MODEL_IOU_THRESHOLD
        self.model = None
        self.image_processor = ImageProcessor()
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model from file."""
        try:
            if Path(self.model_path).exists():
                self.model = YOLO(self.model_path)
                logger.info(f"✓ Loaded trained model from {self.model_path}")
                
                # Verify model classes match
                model_names = self.model.names
                logger.info(f"Model has {len(model_names)} classes: {list(model_names.values())}")
                
                if len(model_names) != 11:
                    logger.warning(f"Expected 11 classes, model has {len(model_names)}")
            else:
                logger.error(f"Model not found at {self.model_path}")
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(
        self, 
        image: np.ndarray,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Detect damages in an image.
        
        Args:
            image: Image as numpy array (RGB format)
            confidence_threshold: Override default confidence threshold
            iou_threshold: Override default IOU threshold
            
        Returns:
            List of detected damages with bounding boxes and metadata
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        conf_thresh = confidence_threshold or self.confidence_threshold
        iou_thresh = iou_threshold or self.iou_threshold
        
        # Run inference
        results = self.model.predict(
            image,
            conf=conf_thresh,
            iou=iou_thresh,
            verbose=False
        )
        
        # Parse results
        detections = self._parse_results(results[0], image.shape)
        
        # Add severity classification and affected parts
        detections = [self._classify_damage(det) for det in detections]
        
        return detections
    
    def _parse_results(self, result, image_shape: Tuple) -> List[Dict]:
        """
        Parse YOLO results into structured format.
        
        Args:
            result: YOLO result object
            image_shape: (height, width, channels)
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        height, width = image_shape[:2]
        
        if result.boxes is None or len(result.boxes) == 0:
            return detections
        
        boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)
        
        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = box
            
            # Convert to [x, y, width, height] format
            bbox_x = x1
            bbox_y = y1
            bbox_width = x2 - x1
            bbox_height = y2 - y1
            
            # Normalize coordinates
            norm_bbox = self.image_processor.normalize_bbox(
                (bbox_x, bbox_y, bbox_width, bbox_height),
                width, height
            )
            
            # Get damage type from model's class names
            damage_type = self.model.names[cls_id]
            
            detection = {
                "damage_type": damage_type,
                "confidence": float(conf),
                "bbox_x": norm_bbox[0],
                "bbox_y": norm_bbox[1],
                "bbox_width": norm_bbox[2],
                "bbox_height": norm_bbox[3],
                "class_id": int(cls_id)
            }
            
            detections.append(detection)
        
        return detections
    
    def _classify_damage(self, detection: Dict) -> Dict:
        """
        Classify damage severity and identify affected part.
        
        Args:
            detection: Detection dictionary
            
        Returns:
            Detection with severity and affected_part added
        """
        damage_type = detection["damage_type"]
        bbox_area = detection["bbox_width"] * detection["bbox_height"]
        
        # Determine severity
        severity = self._determine_severity(damage_type, bbox_area)
        detection["severity"] = severity
        
        # Determine affected part
        affected_part = self._determine_affected_part(detection)
        detection["affected_part"] = affected_part
        
        return detection
    
    def _determine_severity(self, damage_type: str, bbox_area: float) -> str:
        """
        Determine severity based on damage type and size.
        
        Args:
            damage_type: Type of damage
            bbox_area: Normalized area of bounding box (0-1)
            
        Returns:
            Severity level: "minor", "moderate", or "severe"
        """
        # Check if damage type has a fixed severity rule
        if damage_type in self.SEVERITY_RULES:
            fixed_severity = self.SEVERITY_RULES[damage_type]
            if fixed_severity:
                return fixed_severity
        
        # For dent_or_scratch and other variable severities, use size
        if bbox_area > 0.15:  # Large damage (>15% of image)
            return "severe"
        elif bbox_area > 0.05:  # Medium damage (5-15% of image)
            return "moderate"
        else:  # Small damage (<5% of image)
            return "minor"
    
    def _determine_affected_part(self, detection: Dict) -> str:
        """
        Determine which car part is damaged.
        
        Args:
            detection: Detection dictionary with bbox and damage_type
            
        Returns:
            Car part name
        """
        damage_type = detection["damage_type"]
        
        # Check if damage type directly maps to a part
        if damage_type in self.PART_MAPPING:
            part = self.PART_MAPPING[damage_type]
            if part:
                return part
        
        # For dent_or_scratch, infer from position
        return self._infer_part_from_position(detection)
    
    def _infer_part_from_position(self, detection: Dict) -> str:
        """
        Infer car part based on bounding box position in image.
        
        Args:
            detection: Detection dictionary with bbox
            
        Returns:
            Estimated car part name
        """
        x = detection["bbox_x"] + detection["bbox_width"] / 2  # Center X
        y = detection["bbox_y"] + detection["bbox_height"] / 2  # Center Y
        
        # Simple heuristic based on position
        # Assumes car is photographed from side/front view
        
        # Vertical zones
        if y < 0.25:  # Top 25%
            return "roof"
        elif y < 0.5:  # Upper middle
            if x < 0.3:
                return "hood"
            elif x > 0.7:
                return "trunk"
            else:
                return "window"
        elif y < 0.75:  # Lower middle
            if x < 0.3:
                return "front_fender"
            elif x > 0.7:
                return "rear_fender"
            else:
                return "door"
        else:  # Bottom 25%
            if x < 0.5:
                return "front_bumper"
            else:
                return "rear_bumper"
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "model_path": str(self.model_path),
            "model_type": "YOLOv8",
            "num_classes": len(self.DAMAGE_CLASSES),
            "damage_classes": self.DAMAGE_CLASSES,
            "class_names": list(self.DAMAGE_CLASSES.values()),
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold
        }
    
    def get_class_distribution(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Get distribution of detected damage types.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary mapping damage type to count
        """
        distribution = {name: 0 for name in self.DAMAGE_CLASSES.values()}
        
        for det in detections:
            damage_type = det["damage_type"]
            if damage_type in distribution:
                distribution[damage_type] += 1
        
        # Remove zero counts
        return {k: v for k, v in distribution.items() if v > 0}