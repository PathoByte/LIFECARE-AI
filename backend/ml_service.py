import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Dict, Any
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class HealthAnomalyDetector:
    def __init__(self, model_path: str = "models/anomaly_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = ['heart_rate', 'blood_oxygen']
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                logger.info(f"Model loaded from {self.model_path}")
            else:
                self.create_and_train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.create_and_train_model()
    
    def create_and_train_model(self):
        """Create and train a new model with synthetic data"""
        logger.info("Creating new model with synthetic training data")
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 10000
        
        # Normal data
        normal_hr = np.random.normal(75, 15, int(n_samples * 0.9))
        normal_spo2 = np.random.normal(98, 2, int(n_samples * 0.9))
        
        # Anomalous data
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
        
        # Create and train scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Create and train model
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)
        
        # Save model
        self.save_model()
        logger.info("New model created and trained successfully")
    
    def save_model(self):
        """Save the model and scaler"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def predict(self, heart_rate: float, blood_oxygen: float) -> Dict[str, Any]:
        """Make prediction for given health metrics"""
        try:
            # Prepare input data
            X = np.array([[heart_rate, blood_oxygen]])
            X_scaled = self.scaler.transform(X)
            
            # Get anomaly score and prediction
            anomaly_score = self.model.decision_function(X_scaled)[0]
            is_anomaly = self.model.predict(X_scaled)[0] == -1
            
            # Calculate confidence (normalized anomaly score)
            confidence = min(abs(anomaly_score) * 100, 100)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(
                heart_rate, blood_oxygen, is_anomaly, anomaly_score
            )
            
            return {
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly),
                'confidence': float(confidence),
                'recommendations': recommendations
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'anomaly_score': 0.0,
                'is_anomaly': False,
                'confidence': 0.0,
                'recommendations': ['Unable to process prediction. Please try again.']
            }
    
    def generate_recommendations(self, hr: float, spo2: float, is_anomaly: bool, score: float) -> List[str]:
        """Generate health recommendations based on readings"""
        recommendations = []
        
        if is_anomaly:
            if hr < 60:
                recommendations.extend([
                    "⚠️ Low heart rate detected. Consider consulting a healthcare provider.",
                    "💊 Check if you're taking medications that affect heart rate.",
                    "🏃‍♂️ Light physical activity may help increase heart rate."
                ])
            elif hr > 100:
                recommendations.extend([
                    "⚠️ Elevated heart rate detected. Try to rest and relax.",
                    "💧 Ensure adequate hydration.",
                    "🧘‍♀️ Practice deep breathing or meditation."
                ])
            
            if spo2 < 95:
                recommendations.extend([
                    "🚨 Low blood oxygen detected. Seek immediate medical attention if persistent.",
                    "🫁 Practice deep breathing exercises.",
                    "🏥 Consider consulting a healthcare provider."
                ])
        else:
            recommendations.extend([
                "✅ Your vital signs appear normal.",
                "💪 Maintain regular physical activity.",
                "💧 Stay hydrated throughout the day.",
                "😴 Ensure adequate sleep (7-9 hours)."
            ])
        
        return recommendations
    
    def batch_predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """Make predictions for batch data"""
        try:
            X = data[self.feature_names].values
            X_scaled = self.scaler.transform(X)
            
            anomaly_scores = self.model.decision_function(X_scaled)
            predictions = self.model.predict(X_scaled)
            
            data = data.copy()
            data['anomaly_score'] = anomaly_scores
            data['is_anomaly'] = predictions == -1
            
            return data
        
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return data

# Global instance
ml_service = HealthAnomalyDetector()