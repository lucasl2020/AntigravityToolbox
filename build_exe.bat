@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo Starting build for AntigravityToolbox...
echo ============================================================
python scripts/build.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed with code %ERRORLEVEL%!
    pause
    exit /b %ERRORLEVEL%
)
echo ============================================================
echo Build completed successfully!
echo Output directory: dist\AntigravityToolbox\
echo ============================================================
pause
