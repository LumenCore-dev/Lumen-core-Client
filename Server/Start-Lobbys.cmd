@echo off
cd /d "%~dp0"
if exist "%~dp0wide-session.enabled" (
    set "HALO4_CAPACITY_LAB_PLAYERS=128"
    set "HALO4_WIDE_SESSION_BANK=1"
)
"%~dp0Halo4LobbyServer.exe" --dedicated "%~dp0dedicated.cfg"
if errorlevel 1 pause
