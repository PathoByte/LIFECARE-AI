#!/usr/bin/env python3
"""
LifeCare AI Project Setup Script
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_backend():
    """Setup Python backend"""
    print("\n📦 Setting up Python Backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Create necessary directories
    directories = [
        "models",
        "data",
        "data/raw_data",
        "data/raw_data/Heartrate_Data",
        "data/raw_data/SpO2_Data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️ Setting up React Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        os.chdir("..")
        return False
    
    os.chdir("..")
    return True

def create_sample_data():
    """Create sample health data for testing"""
    print("\n📊 Creating sample data...")
    
    sample_data_script = """
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Create sample heart rate data
np.random.seed(42)
dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')

hr_data = []
for date in dates:
    # Normal heart rate with some variation
    base_hr = 75 + np.random.normal(0, 10)
    # Add some anomalies
    if np.random.random() < 0.05:  # 5% anomalies
        base_hr += np.random.choice([-30, 40])  # Very low or high
    
    hr_data.append({
        'Time': date.isoformat(),
        'Value': max(40, min(200, base_hr))  # Clamp to realistic range
    })

hr_df = pd.DataFrame(hr_data)
hr_df.to_csv('data/raw_data/Heartrate_Data/sample_hr.csv', index=False)

# Create sample SpO2 data
spo2_data = []
for date in dates:
    # Normal SpO2 with some variation
    base_spo2 = 98 + np.random.normal(0, 1)
    # Add some anomalies
    if np.random.random() < 0.03:  # 3% anomalies
        base_spo2 -= np.random.uniform(10, 20)  # Low oxygen
    
    spo2_data.append({
        'Time': date.isoformat(),
        'Value': max(70, min(100, base_spo2))  # Clamp to realistic range
    })

spo2_df = pd.DataFrame(spo2_data)
spo2_df.to_csv('data/raw_data/SpO2_Data/sample_spo2.csv', index=False)

print("✅ Sample data created successfully")
"""
    
    try:
        exec(sample_data_script)
        return True
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 LifeCare AI - Project Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        print("⚠️ Sample data creation failed, but continuing...")
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the backend: python run_backend.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    print("\n🔗 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()