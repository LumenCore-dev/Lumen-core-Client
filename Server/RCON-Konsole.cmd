@echo off
setlocal
cd /d "%~dp0"
python "%~dp0rcon_client.py" --host 127.0.0.1 --port 50682 --password-file "%~dp0data\rcon-password.txt"
if errorlevel 1 pause
