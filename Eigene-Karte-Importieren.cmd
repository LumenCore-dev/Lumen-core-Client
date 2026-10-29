@echo off
cd /d "%~dp0"
py -3.12 Source\tools\import_custom_map.py %*
pause
