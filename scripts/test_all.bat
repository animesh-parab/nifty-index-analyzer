@echo off
echo ========================================
echo Testing All Improvements
echo ========================================
echo.

echo Step 1: Testing Enhanced NSE Fetcher...
echo ----------------------------------------
python nse_fetcher_enhanced.py
echo.

echo Step 2: Testing Data Fetcher Improvements...
echo ----------------------------------------
python test_improvements.py
echo.

echo ========================================
echo All Tests Complete!
echo ========================================
echo.
echo If tests passed, run:
echo   streamlit run app.py
echo.
pause
