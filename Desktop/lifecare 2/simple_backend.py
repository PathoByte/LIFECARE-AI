#!/usr/bin/env python3
"""
Simple LifeCare AI Backend - Minimal version without external dependencies
"""
import json
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Simple in-memory storage for demo
users_db = {}
health_data_db = []
alerts_db = []

class LifeCareHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = urlparse(self.path).path
        
        if path == '/health':
            response = {
                "status": "healthy",
                "service": "LifeCare AI Simple Backend",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        elif path == '/api/v1/health/readings':
            response = {
                "readings": health_data_db[-10:],  # Last 10 readings
                "total": len(health_data_db)
            }
        elif path.startswith('/api/v1/health/dashboard/'):
            user_id = path.split('/')[-1]
            user_readings = [r for r in health_data_db if r.get('user_id') == user_id]
            
            if user_readings:
                avg_hr = sum(r['heart_rate'] for r in user_readings) / len(user_readings)
                avg_spo2 = sum(r['blood_oxygen'] for r in user_readings) / len(user_readings)
                anomaly_count = sum(1 for r in user_readings if r.get('is_anomaly', False))
            else:
                avg_hr = avg_spo2 = anomaly_count = 0
            
            response = {
                "recent_readings": user_readings[-20:],
                "metrics": {
                    "avg_heart_rate": round(avg_hr, 1),
                    "avg_blood_oxygen": round(avg_spo2, 1),
                    "anomaly_count": anomaly_count,
                    "total_readings": len(user_readings),
                    "last_reading_time": user_readings[-1]['timestamp'] if user_readings else None
                },
                "alerts": [a for a in alerts_db if a.get('user_id') == user_id][-5:],
                "anomaly_trend": []
            }
        else:
            response = {"message": "LifeCare AI Simple Backend", "endpoints": ["/health", "/api/v1/health/readings"]}
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = urlparse(self.path).path
        
        try:
            data = json.loads(post_data.decode())
        except:
            data = {}
        
        if path == '/api/v1/auth/register':
            user_id = len(users_db) + 1
            username = data.get('username', f'user_{user_id}')
            users_db[username] = {
                "id": user_id,
                "username": username,
                "email": data.get('email', f'{username}@example.com'),
                "full_name": data.get('full_name', username),
                "age": data.get('age'),
                "gender": data.get('gender'),
                "medical_conditions": data.get('medical_conditions'),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            response = users_db[username]
            
        elif path == '/api/v1/auth/login':
            username = data.get('username', 'demo_user')
            # Create demo user if doesn't exist
            if username not in users_db:
                users_db[username] = {
                    "id": len(users_db) + 1,
                    "username": username,
                    "email": f'{username}@example.com',
                    "full_name": username.replace('_', ' ').title(),
                    "age": 30,
                    "gender": "other",
                    "medical_conditions": None,
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
            
            response = {
                "access_token": f"demo_token_{username}_{int(time.time())}",
                "token_type": "bearer",
                "user": users_db[username]
            }
            
        elif path == '/api/v1/health/readings':
            # Simple anomaly detection
            hr = data.get('heart_rate', 75)
            spo2 = data.get('blood_oxygen', 98)
            
            # Basic anomaly rules
            is_anomaly = hr < 60 or hr > 100 or spo2 < 95
            anomaly_score = 0.5 if is_anomaly else -0.5
            
            reading = {
                "id": len(health_data_db) + 1,
                "user_id": data.get('user_id', 'demo_user'),
                "timestamp": datetime.now().isoformat(),
                "heart_rate": hr,
                "blood_oxygen": spo2,
                "temperature": data.get('temperature'),
                "blood_pressure_systolic": data.get('blood_pressure_systolic'),
                "blood_pressure_diastolic": data.get('blood_pressure_diastolic'),
                "activity_level": data.get('activity_level'),
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
                "created_at": datetime.now().isoformat()
            }
            
            health_data_db.append(reading)
            
            # Create alert if anomaly
            if is_anomaly:
                alert = {
                    "id": len(alerts_db) + 1,
                    "user_id": reading['user_id'],
                    "alert_type": "anomaly",
                    "message": f"Anomaly detected: HR={hr}, SpO2={spo2}%",
                    "severity": "high" if hr < 50 or hr > 120 or spo2 < 90 else "medium",
                    "is_read": False,
                    "created_at": datetime.now().isoformat()
                }
                alerts_db.append(alert)
            
            response = reading
            
        elif path == '/api/v1/health/predict':
            hr = data.get('heart_rate', 75)
            spo2 = data.get('blood_oxygen', 98)
            
            is_anomaly = hr < 60 or hr > 100 or spo2 < 95
            confidence = 85 if is_anomaly else 95
            
            recommendations = []
            if is_anomaly:
                if hr < 60:
                    recommendations.extend([
                        "⚠️ Low heart rate detected. Consider consulting a healthcare provider.",
                        "🏃‍♂️ Light physical activity may help increase heart rate."
                    ])
                elif hr > 100:
                    recommendations.extend([
                        "⚠️ Elevated heart rate detected. Try to rest and relax.",
                        "🧘‍♀️ Practice deep breathing or meditation."
                    ])
                if spo2 < 95:
                    recommendations.extend([
                        "🚨 Low blood oxygen detected. Seek medical attention if persistent.",
                        "🫁 Practice deep breathing exercises."
                    ])
            else:
                recommendations.extend([
                    "✅ Your vital signs appear normal.",
                    "💪 Maintain regular physical activity.",
                    "💧 Stay hydrated throughout the day."
                ])
            
            response = {
                "anomaly_score": 0.5 if is_anomaly else -0.5,
                "is_anomaly": is_anomaly,
                "confidence": confidence,
                "recommendations": recommendations
            }
            
        else:
            response = {"message": "Endpoint not found"}
        
        self.wfile.write(json.dumps(response).encode())

def run_server():
    """Run the simple HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, LifeCareHandler)
    
    print("🏥 LifeCare AI Simple Backend")
    print("=" * 40)
    print("🚀 Server running on http://localhost:8000")
    print("📖 Health check: http://localhost:8000/health")
    print("🔗 API endpoints available at /api/v1/")
    print("\n📋 Demo credentials:")
    print("   Username: demo_user")
    print("   Password: any_password")
    print("\n⚠️ This is a simplified demo version")
    print("   For production, install full dependencies")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()