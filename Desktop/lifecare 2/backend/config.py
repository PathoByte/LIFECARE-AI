from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lifecare.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model
    MODEL_PATH: str = "models/anomaly_model.pkl"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LifeCare AI"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()