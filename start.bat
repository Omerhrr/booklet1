@echo off
REM Booklet ERP - Quick Start Script for Windows

echo ==============================================
echo   Booklet ERP - Multi-Tenant SaaS Platform
echo ==============================================
echo.

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Created .env file - please review and update settings
)

REM Initialize database
echo Initializing database...
python run.py init

echo.
echo ==============================================
echo   Setup Complete!
echo ==============================================
echo.
echo To start the application:
echo   python run.py run
echo.
echo Access the application:
echo   Frontend: http://localhost:5000
echo   API Docs: http://localhost:8000/api/docs
echo.
pause
