@echo off
setlocal
cd /d D:\Halo4-Server\Source
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
set "CARGO_HOME=%CD%\build\rust-runtime\cargo"
set "RUSTUP_HOME=%CD%\build\rust-runtime\rustup"
set "PATH=%RUSTUP_HOME%\toolchains\stable-x86_64-pc-windows-msvc\bin;%PATH%"
set "RUSTFLAGS=-C target-feature=+crt-static"
set "CARGO_TARGET_DIR=%CD%\build\session-leave-rust"
cargo test --manifest-path server\Cargo.toml --offline --lib --features wide-session-coordinator
if errorlevel 1 exit /b 1
cargo build --manifest-path server\Cargo.toml --release --offline --lib --features wide-session-coordinator
exit /b %errorlevel%
