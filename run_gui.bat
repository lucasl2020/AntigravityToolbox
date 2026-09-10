@echo off
setlocal
cd /d "%~dp0"
python src/app.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application exited with code %ERRORLEVEL%
    pause
)
