@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Hugegrass-SDK-Test-starten.ps1"
if errorlevel 1 pause
