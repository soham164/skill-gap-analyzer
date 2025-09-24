@echo off
echo ========================================
echo   SKILL GAP ANALYZER - STARTUP SCRIPT
echo ========================================

:: Set colors for better visibility
color 0A

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

:: Setup Python Service
echo.
echo 🐍 Setting up Python Service...
cd python-service

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt

:: Download spaCy model
echo Downloading spaCy English model...
python -m spacy download en_core_web_sm

cd ..

:: Setup Backend
echo.
echo 🚀 Setting up Backend...
cd backend
if exist "package.json" (
    echo Installing backend dependencies...
    npm install
)
cd ..

:: Setup Frontend
echo.
echo ⚛️ Setting up Frontend...
cd frontend
if exist "package.json" (
    echo Installing frontend dependencies...
    npm install
)
cd ..

echo.
echo ✅ All services setup complete!
echo.
echo Starting all services...
echo.

:: Start Python service in background
echo 🐍 Starting Python Service on port 8000...
cd python-service
start "Python Service" cmd /k "venv\Scripts\activate.bat && python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"
cd ..

:: Wait a bit for Python service to start
timeout /t 5 /nobreak >nul

:: Start Backend in background
echo 🚀 Starting Backend on port 5400...
cd backend
start "Backend Service" cmd /k "npm run dev"
cd ..

:: Wait a bit for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend in background
echo ⚛️ Starting Frontend on port 5173...
cd frontend
start "Frontend Service" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo 🎉 ALL SERVICES STARTED!
echo ========================================
echo.
echo 📋 Service URLs:
echo   🐍 Python API:    http://localhost:8000
echo   🚀 Backend API:   http://localhost:5400
echo   ⚛️ Frontend App:   http://localhost:5173
echo.
echo 📖 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check:      http://localhost:8000/api/health
echo.
echo Press any key to open the main application...
pause >nul

:: Open the main application
start http://localhost:5173

echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause