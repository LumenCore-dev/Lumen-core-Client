Lumen Core 0.2.8-preview - Windows x64

EARLY TEST BUILD. Not a stable release.

1. Extract the entire ZIP to its own writable folder, outside Steam/MCC.
2. Start LumenCore.exe (or Start-Client.cmd).
3. Select your Steam MCC folder with Halo 4 installed.
4. Set your player name and start.
5. On the first launch of each version, stay on the loading screen while
   graphics are prepared automatically. Later launches skip this preparation.

Windows 10/11 x64, .NET Framework 4.8, DirectX 11 graphics and your own
supported Steam MCC installation with Halo 4 campaign and multiplayer are
required. Setup checks the engine version. The supported engine SHA-256 is
7c53e7d5bc9848545a1b70e2768242479336fba1b7630d7ab955f7fd0c34fa84.

Setup appears once. It uses German for German Windows display languages and
English otherwise. Client-einrichten.cmd explicitly reopens setup. Some
in-game menus are still German. Existing identity and settings are retained
when updating files in the same client folder; keep reports/native-client.ini
when updating. Never copy someone else's profile or Windows identity key.

The package contains no MCC engine DLL, maps, exported meshes, textures,
personal profiles, server passwords or private keys. Each player uses their
own MCC installation. The bundled standalone preview tool generates Spartan
and Elite previews locally during setup. Allow a few minutes and at least
3 GB of free space during preparation; finished previews use about 705 MB.
Intermediate exports are removed. Later launches reuse the completed files.
Existing 0.2.5 users receive a one-time preparation window on their next start.
No Python or additional .NET runtime installation is required for the tool.
Preview armor changes remain menu-only; they are not replicated in gameplay.
This package includes the
verified public server certificate and matching session profile. The launcher
checks for missing or mixed program files before starting. See Preview-Tool-NOTICES.txt and the matching source ZIP
on the release page.

The native engine backend is NOT fully expanded to 128 players. A 128-slot
session setting is experimental compatibility, not verified 128-player play.
Start with small-group tests. Crashes and connection issues remain possible.
Automatic graphics preparation renders a real local map while keeping the
loading screen visible. Success is saved per client version; failed runs are
retried on the next start. This does not compile every shader for every map.
Files are unsigned.

The default test directory/server is 5.199.139.145, ports 49175/49180.
Report reproducible problems at:
https://github.com/LumenCore-dev/Lumen-core-Client/issues
Include client version, Windows/GPU, map, expected/actual behavior and steps.
Review logs for personal details before sharing them.

Lumen Core Community - Independent community project.
Not affiliated with or endorsed by Microsoft or Halo Studios.
Halo and MCC belong to their respective owners. See NOTICES.md and licenses/.
