from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    ANOMALY = "anomaly"
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class HealthDataCreate(BaseModel):
    user_id: str
    heart_rate: float = Field(..., ge=30, le=220, description="Heart rate in BPM")
    blood_oxygen: float = Field(..., ge=70, le=100, description="Blood oxygen percentage")
    temperature: Optional[float] = Field(None, ge=95, le=110, description="Body temperature in Fahrenheit")
    blood_pressure_systolic: Optional[float] = Field(None, ge=70, le=250)
    blood_pressure_diastolic: Optional[float] = Field(None, ge=40, le=150)
    activity_level: Optional[str] = Field(None, description="low, moderate, high")

class HealthDataResponse(BaseModel):
    id: int
    user_id: str
    timestamp: datetime
    heart_rate: float
    blood_oxygen: float
    temperature: Optional[float]
    blood_pressure_systolic: Optional[float]
    blood_pressure_diastolic: Optional[float]
    activity_level: Optional[str]
    anomaly_score: Optional[float]
    is_anomaly: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, regex=r'^(male|female|other)$')
    medical_conditions: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    age: Optional[int]
    gender: Optional[str]
    medical_conditions: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    user_id: str
    alert_type: AlertType
    message: str
    severity: AlertSeverity

class AlertResponse(BaseModel):
    id: int
    user_id: str
    alert_type: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class HealthMetrics(BaseModel):
    avg_heart_rate: float
    avg_blood_oxygen: float
    anomaly_count: int
    total_readings: int
    last_reading_time: Optional[datetime]

class PredictionRequest(BaseModel):
    heart_rate: float
    blood_oxygen: float
    temperature: Optional[float] = None

class PredictionResponse(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    confidence: float
    recommendations: List[str]

class DashboardData(BaseModel):
    recent_readings: List[HealthDataResponse]
    metrics: HealthMetrics
    alerts: List[AlertResponse]
    anomaly_trend: List[dict]