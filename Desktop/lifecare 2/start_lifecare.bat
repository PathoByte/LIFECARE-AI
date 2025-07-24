@echo off
echo ========================================
echo    LifeCare AI - Healthcare Monitoring
echo ========================================
echo.

echo Installing Python dependencies...
pip install fastapi uvicorn sqlalchemy pandas scikit-learn numpy joblib python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv pydantic

echo.
echo Creating directories...
mkdir models 2>nul
mkdir data 2>nul
mkdir logs 2>nul

echo.
echo Initializing ML model...
python init_model.py

echo.
echo Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo.
echo Starting backend server...
start "LifeCare Backend" python run_backend.py

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting frontend server...
cd frontend
start "LifeCare Frontend" npm start
cd ..

echo.
echo ========================================
echo    LifeCare AI is starting up!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul