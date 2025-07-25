#!/usr/bin/env python3
"""
LifeCare AI - Complete Project Startup Script
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if cwd:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def install_python_deps():
    """Install Python dependencies"""
    print("\n📦 Installing Python Dependencies...")
    
    # Try different pip commands
    pip_commands = [
        "pip install -r requirements.txt",
        "python -m pip install -r requirements.txt",
        "py -m pip install -r requirements.txt"
    ]
    
    for cmd in pip_commands:
        if run_command(cmd, f"Installing Python deps with: {cmd}"):
            return True
    
    # If pip fails, try installing individual packages
    packages = [
        "fastapi", "uvicorn[standard]", "sqlalchemy", "pandas", 
        "scikit-learn", "numpy", "joblib", "python-multipart",
        "python-jose[cryptography]", "passlib[bcrypt]", "python-dotenv", "pydantic"
    ]
    
    for package in packages:
        for pip_cmd in ["pip", "python -m pip", "py -m pip"]:
            if run_command(f"{pip_cmd} install {package}", f"Installing {package}"):
                break
    
    return True

def install_node_deps():
    """Install Node.js dependencies"""
    print("\n⚛️ Installing Node.js Dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Try npm install
    if run_command("npm install", "Installing Node.js dependencies", cwd="frontend"):
        return True
    
    # Try yarn if npm fails
    if run_command("yarn install", "Installing Node.js dependencies with Yarn", cwd="frontend"):
        return True
    
    print("⚠️ Could not install Node.js dependencies. Please install manually.")
    return False

def initialize_model():
    """Initialize the ML model"""
    print("\n🤖 Initializing ML Model...")
    
    # Try different python commands
    python_commands = ["python", "py", "python3"]
    
    for py_cmd in python_commands:
        if run_command(f"{py_cmd} init_model.py", f"Initializing model with {py_cmd}"):
            return True
    
    print("⚠️ Could not initialize ML model. Will create basic model.")
    
    # Create a basic model file if initialization fails
    try:
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        import joblib
        
        # Create basic synthetic data
        np.random.seed(42)
        X_train = np.random.normal([75, 98], [15, 2], (1000, 2))
        
        # Train basic model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_scaled)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_names': ['heart_rate', 'blood_oxygen']
        }
        joblib.dump(model_data, 'models/anomaly_model.pkl')
        print("✅ Basic model created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create basic model: {e}")
        return False

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting Backend Server...")
    
    python_commands = ["python", "py", "python3"]
    
    for py_cmd in python_commands:
        try:
            print(f"Starting backend with {py_cmd}...")
            subprocess.Popen([py_cmd, "run_backend.py"], cwd=".")
            time.sleep(3)  # Give it time to start
            print("✅ Backend server started")
            return True
        except Exception as e:
            print(f"Failed to start with {py_cmd}: {e}")
            continue
    
    print("❌ Could not start backend server")
    return False

def start_frontend():
    """Start the frontend server"""
    print("\n⚛️ Starting Frontend Server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        print("Starting frontend with npm...")
        subprocess.Popen(["npm", "start"], cwd="frontend")
        time.sleep(3)  # Give it time to start
        print("✅ Frontend server started")
        return True
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🏥 LifeCare AI - Complete Project Startup")
    print("=" * 50)
    
    # Create necessary directories
    directories = ["models", "data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Install dependencies
    install_python_deps()
    install_node_deps()
    
    # Initialize ML model
    initialize_model()
    
    # Start servers
    print("\n🚀 Starting Servers...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(5)
    
    # Start frontend
    start_frontend()
    
    print("\n🎉 Project startup completed!")
    print("\n📋 Access Points:")
    print("🌐 Frontend: http://localhost:3000")
    print("🔗 Backend API: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\n⚠️ Note: Servers are running in background. Close terminal to stop.")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")

if __name__ == "__main__":
    main()