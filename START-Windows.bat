@echo off
title Payroll Tools
cd /d "%~dp0"
echo ============================================
echo   Payroll Tools - starting up...
echo ============================================
echo.

REM First run installs the needed Python packages.
python -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo Opening in your browser...
python app.py

echo.
echo Payroll Tools has stopped. Press any key to close.
pause >nul
