@echo off
setlocal
cd /d D:\Halo4-Server\Source
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
set "CARGO_HOME=%CD%\build\rust-runtime\cargo"
set "RUSTUP_HOME=%CD%\build\rust-runtime\rustup"
set "PATH=%RUSTUP_HOME%\toolchains\stable-x86_64-pc-windows-msvc\bin;%PATH%"
set "RUSTFLAGS=-C target-feature=+crt-static"
set "CARGO_TARGET_DIR=%CD%\build\current-rust"
cargo test --manifest-path server\Cargo.toml --offline --lib
if errorlevel 1 exit /b 1
cargo build --manifest-path server\Cargo.toml --release --offline
if errorlevel 1 exit /b 1
if not exist build\public-test mkdir build\public-test
set "COMMON=/nologo /std:c++20 /EHsc /utf-8 /W4 /O2 /MT /DUNICODE /D_UNICODE"
set "LIBS=advapi32.lib bcrypt.lib crypt32.lib version.lib dbghelp.lib user32.lib gdi32.lib shell32.lib d3d11.lib dxgi.lib d2d1.lib dwrite.lib windowscodecs.lib ole32.lib ws2_32.lib ntdll.lib userenv.lib synchronization.lib winmm.lib"
cl %COMMON% server\tests\secure_transport.cpp /Fo"build\public-test\\" /Fe"build\public-test\secure_transport.exe" /link %LIBS%
if errorlevel 1 exit /b 1
build\public-test\secure_transport.exe
if errorlevel 1 exit /b 1
cl %COMMON% native\native_client.cpp build\current\client.res /Fo"build\public-test\\" /Fe"build\public-test\Halo4NativeClient.exe" /link /SUBSYSTEM:WINDOWS /MANIFEST:NO %LIBS%
if errorlevel 1 exit /b 1
cl %COMMON% native\native_server.cpp build\current\client.res /Fo"build\public-test\\" /Fe"build\public-test\Halo4DedicatedServer.exe" /link /SUBSYSTEM:WINDOWS /MANIFEST:NO /STACK:8388608 build\current-rust\release\halo4_server_core.lib %LIBS%
exit /b %errorlevel%
