@echo off
title Antigravity Proxy Checker
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_antigravity_proxy.ps1" %*
echo.
pause
