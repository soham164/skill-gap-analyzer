@echo off
echo Starting Python Service...
cd python-service
start "Python API Service" cmd /k "python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"
echo Python service started on http://localhost:8000
timeout /t 3 /nobreak >nul
echo.
echo Python service is running in a separate window.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health