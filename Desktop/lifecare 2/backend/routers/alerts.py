from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db, Alert, User
from ..models import AlertCreate, AlertResponse
from ..auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert"""
    try:
        db_alert = Alert(
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            message=alert.message,
            severity=alert.severity
        )
        
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        return db_alert
    
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        )

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    user_id: Optional[str] = None,
    is_read: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts for a user"""
    query = db.query(Alert)
    
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@router.put("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an alert as read"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.is_read = True
        db.commit()
        
        return {"message": "Alert marked as read"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark alert as read"
        )

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alert"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        db.delete(alert)
        db.commit()
        
        return {"message": "Alert deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert"
        )