@echo off
setlocal
echo ==========================================
echo VEDA TECHNOLOGY - TASK 29 SETUP
echo ==========================================
py -3.12 -m venv .venv
if errorlevel 1 (
  echo Python 3.12 was not found. Install Python 3.12+ and run this file again.
  pause
  exit /b 1
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete.
echo Start the app with: start_app.bat
pause
