import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import io


class ImageProcessor:
    """Handles image preprocessing for ML model inference."""
    
    @staticmethod
    def validate_image(image_bytes: bytes) -> bool:
        """
        Validate that bytes represent a valid image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            Image.open(io.BytesIO(image_bytes))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """
        Load image from file path.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array in RGB format
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        # Convert BGR to RGB
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """
        Load image from bytes.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Image as numpy array in RGB format
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode image from bytes")
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
        """
        Get image width and height.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (width, height)
        """
        height, width = image.shape[:2]
        return width, height
    
    @staticmethod
    def resize_image(
        image: np.ndarray, 
        target_size: Optional[Tuple[int, int]] = None,
        max_dimension: Optional[int] = None
    ) -> np.ndarray:
        """
        Resize image to target size or max dimension.
        
        Args:
            image: Image as numpy array
            target_size: Exact (width, height) to resize to
            max_dimension: Maximum dimension while maintaining aspect ratio
            
        Returns:
            Resized image
        """
        if target_size:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
        
        if max_dimension:
            height, width = image.shape[:2]
            if max(height, width) > max_dimension:
                if height > width:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))
                else:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    @staticmethod
    def normalize_bbox(
        bbox: Tuple[float, float, float, float],
        image_width: int,
        image_height: int
    ) -> Tuple[float, float, float, float]:
        """
        Normalize bounding box coordinates to 0-1 range.
        
        Args:
            bbox: (x, y, width, height) in pixels
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            Normalized (x, y, width, height)
        """
        x, y, w, h = bbox
        return (
            x / image_width,
            y / image_height,
            w / image_width,
            h / image_height
        )
    
    @staticmethod
    def denormalize_bbox(
        bbox: Tuple[float, float, float, float],
        image_width: int,
        image_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Convert normalized bounding box to pixel coordinates.
        
        Args:
            bbox: Normalized (x, y, width, height) in 0-1 range
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            (x, y, width, height) in pixels
        """
        x, y, w, h = bbox
        return (
            int(x * image_width),
            int(y * image_height),
            int(w * image_width),
            int(h * image_height)
        )
    
    @staticmethod
    def draw_detections(
        image: np.ndarray,
        detections: list,
        confidence_threshold: float = 0.5
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on image.
        
        Args:
            image: Image as numpy array
            detections: List of detection dicts with bbox and label info
            confidence_threshold: Minimum confidence to draw
            
        Returns:
            Image with drawn detections
        """
        result_image = image.copy()
        height, width = image.shape[:2]
        
        for det in detections:
            if det.get('confidence', 0) < confidence_threshold:
                continue
            
            # Denormalize bbox
            x, y, w, h = ImageProcessor.denormalize_bbox(
                (det['bbox_x'], det['bbox_y'], det['bbox_width'], det['bbox_height']),
                width, height
            )
            
            # Draw rectangle
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label
            label = f"{det['damage_type']} ({det['confidence']:.2f})"
            cv2.putText(
                result_image, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        return result_image