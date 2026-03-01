@echo off
echo ==================================
echo Nifty AI Predictor - Quick Test
echo ==================================
echo.

REM Test 1: Check Python
echo 1. Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo    X Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo    √ Python OK
echo.

REM Test 2: Check dependencies
echo 2. Checking dependencies...
pip list | findstr streamlit >nul 2>&1
if errorlevel 1 (
    echo    ! Dependencies not installed
    echo    Installing now...
    pip install -r requirements.txt
)
echo    √ Dependencies OK
echo.

REM Test 3: Test NSE Fetcher
echo 3. Testing NSE API...
python nse_fetcher_enhanced.py
echo.

REM Test 4: Check Groq API key
echo 4. Checking Groq API key...
if exist .env (
    findstr "GROQ_API_KEY=your_groq_api_key_here" .env >nul 2>&1
    if not errorlevel 1 (
        echo    ! Groq API key not set
        echo    Edit .env file and add your key from https://console.groq.com
    ) else (
        echo    √ Groq API key configured
    )
) else (
    echo    ! .env file not found
    echo    Run: copy env.example .env
    echo    Then edit .env and add your Groq API key
)
echo.

echo ==================================
echo Setup complete!
echo ==================================
echo.
echo To start the dashboard:
echo   streamlit run app.py
echo.
echo To test with sample data:
echo   python create_sample_data.py
echo   streamlit run app_dry_run.py
echo.
pause
