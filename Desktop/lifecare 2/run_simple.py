#!/usr/bin/env python3
"""
Simple LifeCare AI Startup - No external dependencies required
"""
import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

def start_backend():
    """Start the simple backend server"""
    print("🚀 Starting LifeCare AI Simple Backend...")
    try:
        # Import and run the simple backend
        import simple_backend
        simple_backend.run_server()
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def open_frontend():
    """Open the frontend in the default browser"""
    time.sleep(2)  # Wait for backend to start
    frontend_path = Path("simple_frontend.html").absolute()
    
    if frontend_path.exists():
        print(f"🌐 Opening frontend: {frontend_path}")
        webbrowser.open(f"file://{frontend_path}")
    else:
        print("❌ Frontend file not found")

def main():
    """Main function"""
    print("🏥 LifeCare AI - Simple Version")
    print("=" * 40)
    print("📋 This is a simplified version that works without external dependencies")
    print("📦 For the full version, install the requirements and use the React frontend")
    print("=" * 40)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Open frontend after a short delay
    frontend_thread = threading.Thread(target=open_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    print("\n🎉 LifeCare AI is starting!")
    print("\n📋 Access Points:")
    print("🌐 Frontend: Will open automatically in your browser")
    print("🔗 Backend API: http://localhost:8000")
    print("📖 Health Check: http://localhost:8000/health")
    print("\n📝 Demo Credentials:")
    print("   Username: demo_user")
    print("   Password: any_password")
    print("\n⚠️ Note: This is a demo version with in-memory storage")
    print("💡 For production use, install full dependencies and use the complete version")
    print("\nPress Ctrl+C to stop the servers")
    print("=" * 40)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down LifeCare AI...")
        print("👋 Thank you for using LifeCare AI!")

if __name__ == "__main__":
    main()