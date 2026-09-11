@echo off
rem Tempora installer wrapper: runs install.ps1 without execution-policy friction.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
pause
