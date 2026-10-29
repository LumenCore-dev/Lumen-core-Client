@echo off
setlocal
cd /d "%~dp0"
python "%~dp0Source\webpanel\app.py" --open
if errorlevel 1 pause
