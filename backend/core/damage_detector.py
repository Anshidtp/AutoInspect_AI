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
    Detects various types of car damage and classifies severity.
    """
    
    # Damage type mappings (customize based on your trained model)
    DAMAGE_CLASSES = {
        0: "dent",
        1: "scratch",
        2: "crack",
        3: "broken_light",
        4: "broken_windshield",
        5: "broken_mirror",
        6: "flat_tire",
        7: "bumper_damage"
    }
    
    # Car part detection (optional, if your model supports it)
    CAR_PARTS = {
        "front_bumper", "rear_bumper", "hood", "door", 
        "fender", "mirror", "headlight", "taillight",
        "windshield", "window", "tire", "wheel"
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
        
        # Load model if path exists
        if Path(self.model_path).exists():
            self._load_model()
        else:
            logger.warning(f"Model not found at {self.model_path}. Using default YOLOv8n.")
            self.model = YOLO('yolov8n.pt')  # Fallback to pretrained model
    
    def _load_model(self):
        """Load YOLO model from file."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded YOLO model from {self.model_path}")
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
        
        # Add severity classification
        detections = [self._classify_severity(det) for det in detections]
        
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
            
            # Get damage type
            damage_type = self.DAMAGE_CLASSES.get(cls_id, f"unknown_{cls_id}")
            
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
    
    def _classify_severity(self, detection: Dict) -> Dict:
        """
        Classify damage severity based on type and size.
        
        Args:
            detection: Detection dictionary
            
        Returns:
            Detection with severity added
        """
        damage_type = detection["damage_type"]
        bbox_area = detection["bbox_width"] * detection["bbox_height"]
        
        # Severity rules (customize based on your requirements)
        if damage_type in ["broken_windshield", "broken_light"]:
            severity = "severe"
        elif damage_type in ["crack", "broken_mirror"]:
            severity = "moderate"
        elif bbox_area > 0.1:  # Large damage area
            severity = "severe"
        elif bbox_area > 0.05:
            severity = "moderate"
        else:
            severity = "minor"
        
        detection["severity"] = severity
        
        # Infer affected part (basic heuristic based on position)
        detection["affected_part"] = self._infer_car_part(detection)
        
        return detection
    
    def _infer_car_part(self, detection: Dict) -> Optional[str]:
        """
        Infer which car part is damaged based on bbox position.
        
        Args:
            detection: Detection dictionary with bbox
            
        Returns:
            Estimated car part name or None
        """
        x, y = detection["bbox_x"], detection["bbox_y"]
        damage_type = detection["damage_type"]
        
        # Simple heuristic based on vertical position
        if damage_type == "broken_windshield":
            return "windshield"
        elif damage_type in ["broken_light", "headlight"]:
            return "headlight" if y < 0.5 else "taillight"
        elif damage_type == "flat_tire":
            return "tire"
        elif damage_type == "broken_mirror":
            return "mirror"
        elif y < 0.3:  # Top third
            return "hood" if x < 0.5 else "roof"
        elif y < 0.7:  # Middle third
            return "door"
        else:  # Bottom third
            return "front_bumper" if x < 0.5 else "rear_bumper"
        
        return None
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "model_path": str(self.model_path),
            "model_type": "YOLOv11",
            "num_classes": len(self.DAMAGE_CLASSES),
            "damage_classes": self.DAMAGE_CLASSES,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold
        }