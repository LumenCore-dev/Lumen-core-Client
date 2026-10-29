@echo off
call "%~dp0Source\Build-Aktuell.cmd"
if errorlevel 1 (echo Build fehlgeschlagen. & pause & exit /b 1)
echo Client und Server wurden aktualisiert.
pause
