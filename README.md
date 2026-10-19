# Lumen Core

Community client for Halo 4 on PC. Early preview for small-group testing.
Requires your own supported Steam MCC installation with Halo 4 campaign and
multiplayer. Windows 10/11 x64, .NET Framework 4.8 and DirectX 11 are required.

Download **0.2.10-preview** from [Releases](https://github.com/LumenCore-dev/Lumen-core-Client/releases).
Extract the complete ZIP into a writable folder outside Steam/MCC and start
`LumenCore.exe`. Keep the certificate, build/session files and preview tool.

This public release uses original maps from the user's local MCC installation.
**Custom Elite gameplay and custom emotes are paused.** Setup can still create
menu previews locally; this does not activate those gameplay features. Global
and team text chat, configurable communication shortcuts and voice settings
are included. A 128-slot configuration is experimental; working simultaneous
128-player gameplay is not claimed. Builds are unsigned.

First startup selects MCC and prepares local previews and graphics. Allow
about 3 GB free during preview preparation. The standalone preview tool has
its runtime included. Successful local preparation is reused. Use
`Client-einrichten.cmd` to reopen setup. Keep your existing
`reports/native-client.ini` when updating; do not share identity/private keys.

The download includes no MCC engine DLL, game maps, generated Halo models,
textures or loading artwork. Setup reads the user's files and writes generated
previews in the separate client directory. Program-owned text/colors are used
for setup and loading screens. Matching GPL preview-tool source and notices
are supplied with the release; the preview tool is unchanged from 0.2.9.

This publication was packaged and statically checked; no new gameplay test
was run for publication. See the included README, notices and release notes.
Report reproducible issues with version, map, Windows/GPU, steps and expected
versus actual behavior at [Issues](https://github.com/LumenCore-dev/Lumen-core-Client/issues).
Review personal details before sharing logs.

Independent community project, not affiliated with or endorsed by Microsoft
or Halo Studios. Halo and MCC belong to their owners.

## Run your own server

A separate [Dedicated Server 0.2.10-preview](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/server-v0.2.10-preview)
package is available for Windows x64 and Linux x86_64 via Wine 11.
Read the [German setup/upload/configuration guide](SERVER-ANLEITUNG.md).
The package includes a fresh example configuration and setup tools; operators
supply their own local MCC data. No game assets, operator credentials, private
keys, databases or populated administrator lists are bundled. Elite and custom
emotes remain paused. Native compatibility: 0.2.8; matching client: 0.2.10-preview.
