@echo off
echo ========================================
echo    LifeCare AI - Windows Deployment
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed
echo.

REM Create necessary directories
echo ℹ️ Creating necessary directories...
mkdir data 2>nul
mkdir models 2>nul
mkdir logs 2>nul
echo ✅ Directories created
echo.

REM Build and start services
echo ℹ️ Building and starting LifeCare AI services...
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

REM Wait for services to start
echo ℹ️ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check backend health
echo ℹ️ Checking backend health...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is healthy
) else (
    echo ❌ Backend health check failed
    docker-compose logs backend
    pause
    exit /b 1
)

REM Display deployment information
echo.
echo 🎉 LifeCare AI Deployment Complete!
echo ==================================
echo.
echo 📋 Access Information:
echo 🌐 Frontend:     http://localhost:3000
echo 🔗 Backend API:  http://localhost:8000
echo 📖 API Docs:     http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo.
echo 📊 Container Status:
docker-compose ps
echo.
echo 📝 Demo Credentials:
echo    Username: demo_user
echo    Password: any_password
echo.
echo 🔧 Management Commands:
echo    Stop services:    docker-compose down
echo    View logs:        docker-compose logs -f
echo    Restart:          docker-compose restart
echo    Update:           deploy.bat
echo.
echo ✅ LifeCare AI is now running in production mode!
echo.

REM Open browser
echo ℹ️ Opening LifeCare AI in browser...
start http://localhost:3000

echo Press any key to exit...
pause >nul