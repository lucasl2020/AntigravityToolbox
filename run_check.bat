@echo off
title Antigravity Proxy Checker
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0legacy\check_antigravity_proxy.ps1" %*
echo.
pause
