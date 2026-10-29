@echo off
setlocal
cd /d D:\Halo4-Server\Source
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
if not exist build\deadlock mkdir build\deadlock
cl /nologo /std:c++20 /EHsc /utf-8 /W4 /Zi /O2 /MT /DUNICODE /D_UNICODE /FI"D:\Halo4-Server\reports\linux-vps-20261016\cpp-exception-trace.hpp" native\native_client.cpp build\current\client.res /Fo"build\deadlock\\" /Fd"build\deadlock\compile.pdb" /Fe"build\deadlock\Halo4NativeClient.exe" /link /DEBUG:FULL /PDB:"build\deadlock\Halo4NativeClient.pdb" /SUBSYSTEM:WINDOWS /MANIFEST:NO advapi32.lib bcrypt.lib crypt32.lib version.lib dbghelp.lib user32.lib gdi32.lib shell32.lib d3d11.lib dxgi.lib d2d1.lib dwrite.lib windowscodecs.lib ole32.lib ws2_32.lib ntdll.lib userenv.lib synchronization.lib winmm.lib
exit /b %errorlevel%
