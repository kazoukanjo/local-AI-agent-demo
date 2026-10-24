@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Tao moi truong Python...
 python -m venv .venv
 if errorlevel 1 pause & exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" -m playwright install chromium
".venv\Scripts\python.exe" main.py
pause
