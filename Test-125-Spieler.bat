@echo off
setlocal EnableExtensions
rem ===================================================================
rem  Backend128 / 125-Spieler-Test  (ohne Desktop-Steuerung)
rem  1) isolierter Build   2) Test mit echten + Kontroll-Clients
rem  3) nur bei BESTANDEN und nach Rueckfrage: Client + Server aktualisieren
rem
rem  Aufruf:  Test-125-Spieler.bat [sicher|offen] [echte_clients] [sekunden] [ohnebuild]
rem    sicher = Backend128-Schalter zu (Standard, Verhalten wie bisher + Registrierung)
rem    offen  = experimentell: alle Backend128-Pfade aktiv (echte >16 Verbindungen)
rem ===================================================================
cd /d "%~dp0Source"
set "VARIANT=%~1"
if "%VARIANT%"=="" set "VARIANT=sicher"
set "REAL=%~2"
if "%REAL%"=="" set "REAL=2"
set "HOLD=%~3"
if "%HOLD%"=="" set "HOLD=240"
set "OUT=%CD%\build\b128-test\%VARIANT%"
set "REPORT=%CD%\reports\b128-test\%VARIANT%\result.json"
set "CL="
if /i "%VARIANT%"=="offen" set "CL=/DHALO4_BACKEND128_CLOSED"

echo.
echo === Speicherplatz pruefen ===
powershell -NoProfile -Command "if ((Get-PSDrive '%~d0'.TrimEnd(':')).Free -lt 15GB) { Write-Host 'Weniger als 15 GB frei - Abbruch.'; exit 1 }"
if errorlevel 1 goto fail

echo.
if /i "%~4"=="ohnebuild" if exist "%OUT%\bin\Halo4DedicatedServer.exe" (echo Build uebersprungen. & goto test)
echo === 1/3 Isolierter Build (%VARIANT%) nach %OUT% ===
python tools\emote-inspect\build_wide.py --skip-tests --output-root "%OUT%"
if errorlevel 1 (
  echo Build fehlgeschlagen. Log: %OUT%\native\build.log
  goto fail
)
rem Objektdateien loeschen, nur EXE/DLL behalten (HDD)
if exist "%OUT%\native\Client" rmdir /s /q "%OUT%\native\Client"
if exist "%OUT%\native\Runtime" rmdir /s /q "%OUT%\native\Runtime"
if exist "%OUT%\native\DedicatedServer" rmdir /s /q "%OUT%\native\DedicatedServer"

:test
echo.
echo === Python-Paket fuer Kontroll-Clients pruefen ===
python -c "import cryptography" 2>nul
if errorlevel 1 (
  echo Installiere Paket 'cryptography' fuer python ...
  python -m pip install --user cryptography
  python -c "import cryptography" 2>nul
  if errorlevel 1 (echo Installation fehlgeschlagen. & goto fail)
)
echo.
echo === 2/3 Test: 125 Spieler (%REAL% echte Clients, Rest Kontroll-Clients), %HOLD% s ===
python tools\test_125.py --build "%OUT%\bin" --players 125 --real-clients %REAL% --hold %HOLD% --report "%REPORT%"
if errorlevel 1 (
  echo TEST NICHT BESTANDEN. Bericht: %REPORT%
  echo Installierte Client/Server wurden NICHT veraendert.
  goto fail
)

echo.
echo === 3/3 Test BESTANDEN ===
choice /c JN /m "Client und Server jetzt mit diesem Stand aktualisieren"
if errorlevel 2 (
  echo Nicht aktualisiert. Build liegt in %OUT%\bin
  goto done
)
call "%CD%\Build-Aktuell.cmd"
if errorlevel 1 (
  echo Aktualisierung fehlgeschlagen.
  goto fail
)
echo Client und Server wurden aktualisiert (%VARIANT%).

:done
set "CL="
pause
exit /b 0
:fail
set "CL="
pause
exit /b 1
