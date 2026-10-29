@echo off
cd /d "%~dp0Client"
start "" "%~dp0Client\Halo4NativeClient.exe" --join-lobby 5.199.139.145:49180 --master-address 5.199.139.145:49175
