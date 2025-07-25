from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class HealthData(Base):
    __tablename__ = "health_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Float)
    blood_oxygen = Column(Float)
    temperature = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Float, nullable=True)
    blood_pressure_diastolic = Column(Float, nullable=True)
    activity_level = Column(String, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    medical_conditions = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    alert_type = Column(String)  # 'anomaly', 'critical', 'warning'
    message = Column(String)
    severity = Column(String)  # 'low', 'medium', 'high', 'critical'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)