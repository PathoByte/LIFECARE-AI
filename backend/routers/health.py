from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db, HealthData, Alert, User
from ..models import (
    HealthDataCreate, HealthDataResponse, PredictionRequest, 
    PredictionResponse, HealthMetrics, DashboardData, AlertResponse
)
from ..ml_service import ml_service
from ..auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

@router.post("/readings", response_model=HealthDataResponse)
async def create_health_reading(
    reading: HealthDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new health reading and analyze for anomalies"""
    try:
        # Get ML prediction
        prediction = ml_service.predict(reading.heart_rate, reading.blood_oxygen)
        
        # Create health data record
        db_reading = HealthData(
            user_id=reading.user_id,
            heart_rate=reading.heart_rate,
            blood_oxygen=reading.blood_oxygen,
            temperature=reading.temperature,
            blood_pressure_systolic=reading.blood_pressure_systolic,
            blood_pressure_diastolic=reading.blood_pressure_diastolic,
            activity_level=reading.activity_level,
            anomaly_score=prediction['anomaly_score'],
            is_anomaly=prediction['is_anomaly']
        )
        
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        
        # Create alert if anomaly detected
        if prediction['is_anomaly']:
            alert = Alert(
                user_id=reading.user_id,
                alert_type="anomaly",
                message=f"Anomaly detected: HR={reading.heart_rate}, SpO2={reading.blood_oxygen}%",
                severity="high" if prediction['confidence'] > 80 else "medium"
            )
            db.add(alert)
            db.commit()
        
        return db_reading
    
    except Exception as e:
        logger.error(f"Error creating health reading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create health reading"
        )

@router.get("/readings", response_model=List[HealthDataResponse])
async def get_health_readings(
    user_id: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get health readings for a user"""
    query = db.query(HealthData)
    
    if user_id:
        query = query.filter(HealthData.user_id == user_id)
    
    readings = query.order_by(HealthData.timestamp.desc()).offset(skip).limit(limit).all()
    return readings

@router.get("/readings/{reading_id}", response_model=HealthDataResponse)
async def get_health_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific health reading"""
    reading = db.query(HealthData).filter(HealthData.id == reading_id).first()
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health reading not found"
        )
    return reading

@router.post("/predict", response_model=PredictionResponse)
async def predict_anomaly(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """Get anomaly prediction for given health metrics"""
    try:
        prediction = ml_service.predict(request.heart_rate, request.blood_oxygen)
        return PredictionResponse(**prediction)
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make prediction"
        )

@router.get("/metrics/{user_id}", response_model=HealthMetrics)
async def get_health_metrics(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get health metrics summary for a user"""
    try:
        # Get readings from last N days
        since_date = datetime.utcnow() - timedelta(days=days)
        readings = db.query(HealthData).filter(
            HealthData.user_id == user_id,
            HealthData.timestamp >= since_date
        ).all()
        
        if not readings:
            return HealthMetrics(
                avg_heart_rate=0,
                avg_blood_oxygen=0,
                anomaly_count=0,
                total_readings=0,
                last_reading_time=None
            )
        
        # Calculate metrics
        avg_hr = sum(r.heart_rate for r in readings) / len(readings)
        avg_spo2 = sum(r.blood_oxygen for r in readings) / len(readings)
        anomaly_count = sum(1 for r in readings if r.is_anomaly)
        last_reading = max(readings, key=lambda x: x.timestamp)
        
        return HealthMetrics(
            avg_heart_rate=round(avg_hr, 1),
            avg_blood_oxygen=round(avg_spo2, 1),
            anomaly_count=anomaly_count,
            total_readings=len(readings),
            last_reading_time=last_reading.timestamp
        )
    
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health metrics"
        )

@router.get("/dashboard/{user_id}", response_model=DashboardData)
async def get_dashboard_data(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard data for a user"""
    try:
        # Get recent readings (last 24 hours)
        since_24h = datetime.utcnow() - timedelta(hours=24)
        recent_readings = db.query(HealthData).filter(
            HealthData.user_id == user_id,
            HealthData.timestamp >= since_24h
        ).order_by(HealthData.timestamp.desc()).limit(50).all()
        
        # Get metrics (last 7 days)
        metrics = await get_health_metrics(user_id, 7, db, current_user)
        
        # Get recent alerts
        alerts = db.query(Alert).filter(
            Alert.user_id == user_id
        ).order_by(Alert.created_at.desc()).limit(10).all()
        
        # Get anomaly trend (last 7 days)
        since_7d = datetime.utcnow() - timedelta(days=7)
        anomaly_readings = db.query(HealthData).filter(
            HealthData.user_id == user_id,
            HealthData.timestamp >= since_7d
        ).all()
        
        # Group by day for trend
        anomaly_trend = []
        for i in range(7):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_readings = [r for r in anomaly_readings 
                          if day_start <= r.timestamp < day_end]
            anomaly_count = sum(1 for r in day_readings if r.is_anomaly)
            
            anomaly_trend.append({
                'date': day_start.isoformat(),
                'anomaly_count': anomaly_count,
                'total_readings': len(day_readings)
            })
        
        return DashboardData(
            recent_readings=recent_readings,
            metrics=metrics,
            alerts=alerts,
            anomaly_trend=list(reversed(anomaly_trend))
        )
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )