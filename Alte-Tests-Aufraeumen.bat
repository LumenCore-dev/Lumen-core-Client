@echo off
setlocal
title Halo4 - Alte Testkopien aufraeumen
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Alte-Tests-Aufraeumen.ps1"
echo.
pause
