@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH.
    echo Please install Python or add it to PATH, then run this file again.
    pause
    exit /b 1
)

python -m streamlit run "%~dp0aiai_seedance2_frontend.py"

if errorlevel 1 (
    echo.
    echo Streamlit failed to start. See the error above.
    pause
)
