#!/usr/bin/env python3
"""
Initialize the ML model for LifeCare AI
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pathlib import Path

def create_synthetic_data():
    """Create synthetic health data for training"""
    print("🔄 Creating synthetic training data...")
    
    np.random.seed(42)
    n_samples = 10000
    
    # Normal data (90%)
    normal_hr = np.random.normal(75, 15, int(n_samples * 0.9))
    normal_spo2 = np.random.normal(98, 2, int(n_samples * 0.9))
    
    # Anomalous data (10%)
    anomaly_hr = np.concatenate([
        np.random.normal(45, 5, int(n_samples * 0.05)),  # Low HR
        np.random.normal(150, 10, int(n_samples * 0.05))  # High HR
    ])
    anomaly_spo2 = np.concatenate([
        np.random.normal(85, 3, int(n_samples * 0.05)),  # Low SpO2
        np.random.normal(85, 3, int(n_samples * 0.05))   # Low SpO2
    ])
    
    # Combine data
    X_train = np.column_stack([
        np.concatenate([normal_hr, anomaly_hr]),
        np.concatenate([normal_spo2, anomaly_spo2])
    ])
    
    # Ensure realistic ranges
    X_train[:, 0] = np.clip(X_train[:, 0], 30, 220)  # Heart rate
    X_train[:, 1] = np.clip(X_train[:, 1], 70, 100)  # SpO2
    
    return X_train

def train_model():
    """Train the anomaly detection model"""
    print("🤖 Training anomaly detection model...")
    
    # Create training data
    X_train = create_synthetic_data()
    
    # Create and train scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # Create and train model
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        max_features=1.0
    )
    model.fit(X_scaled)
    
    # Save model and scaler
    os.makedirs('models', exist_ok=True)
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': ['heart_rate', 'blood_oxygen']
    }
    
    joblib.dump(model_data, 'models/anomaly_model.pkl')
    print("✅ Model trained and saved to models/anomaly_model.pkl")
    
    # Test the model
    test_normal = np.array([[75, 98]])
    test_anomaly = np.array([[45, 85]])
    
    test_normal_scaled = scaler.transform(test_normal)
    test_anomaly_scaled = scaler.transform(test_anomaly)
    
    normal_score = model.decision_function(test_normal_scaled)[0]
    anomaly_score = model.decision_function(test_anomaly_scaled)[0]
    
    print(f"📊 Test Results:")
    print(f"   Normal reading (HR:75, SpO2:98) - Score: {normal_score:.3f}")
    print(f"   Anomaly reading (HR:45, SpO2:85) - Score: {anomaly_score:.3f}")
    
    return True

if __name__ == "__main__":
    print("🏥 LifeCare AI - Model Initialization")
    print("=" * 40)
    
    try:
        train_model()
        print("\n🎉 Model initialization completed successfully!")
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        exit(1)