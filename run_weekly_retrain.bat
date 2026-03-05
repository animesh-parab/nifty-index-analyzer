@echo off
REM Batch file to run weekly XGBoost retraining
REM This file is called by Windows Task Scheduler every Sunday at 8 PM

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Activate conda environment if needed (uncomment and modify if using conda)
REM call conda activate your_env_name

REM Run the weekly retraining script
python weekly_retrain.py

REM Pause only if there was an error (for debugging)
if errorlevel 1 (
    echo.
    echo ERROR: Weekly retraining failed!
    echo Check logs/retraining/ for details
    pause
)
