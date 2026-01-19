from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Car Damage Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    
    # ML Model
    MODEL_PATH: str = "model/best.pt"
    MODEL_CONFIDENCE_THRESHOLD: float = 0.5
    MODEL_IOU_THRESHOLD: float = 0.45
    
    # Cost Estimation
    DAMAGE_COSTS_PATH: str = "./data/damage_costs.json"
    LABOR_RATE_PER_HOUR: float = 75.0
    MARKUP_PERCENTAGE: float = 20.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./data", exist_ok=True)
os.makedirs("./ml_models", exist_ok=True)