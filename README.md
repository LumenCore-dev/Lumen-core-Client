# Lumen Core — Halo 4 Multiplayer Client & Dedicated Server for PC

Lumen Core is an independent community project for **Halo 4 multiplayer on PC**,
with a Windows client, a server browser and a separate **Halo 4 dedicated server**
package for Windows and Linux via Wine. It is an early preview for small-group testing.
You need your own supported **Steam Halo: The Master Chief Collection (MCC)**
installation with Halo 4 campaign and multiplayer installed.

[Download the Windows client](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.10-preview/LumenCore-0.2.10-preview-win64.zip)
· [Host your own server](#run-your-own-server-halo-4-dedicated-server)
· [Deutsch](README.de.md)
· [Report an issue](https://github.com/LumenCore-dev/Lumen-core-Client/issues)

## Downloads

| What you want to do | Download | Platform |
|---|---|---|
| Join a Halo 4 multiplayer server | [Client 0.2.10-preview ZIP](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.10-preview/LumenCore-0.2.10-preview-win64.zip) | Windows 10/11 x64 |
| Host a Halo 4 dedicated server | [Server 0.2.10-preview ZIP](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/server-v0.2.10-preview/LumenCore-Server-0.2.10-preview.zip) | Windows x64 or Linux x86_64 with Wine 11 |

Read the [client release notes and checksums](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.10-preview)
or the [server release notes and checksums](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/server-v0.2.10-preview)
before installing. The preview-tool source ZIP is for developers; players need the **win64 ZIP**.

## Play Halo 4 multiplayer on PC

1. Install your own supported Steam MCC copy, including Halo 4 campaign and multiplayer.
2. Extract the **complete client ZIP** into a writable folder outside Steam/MCC.
3. Start **`LumenCore.exe`**, select your MCC installation and complete player setup.
4. Let the first-start preparation finish, then use the server browser to connect to a configured server.

The client requires **Windows 10/11 x64, .NET Framework 4.8 and DirectX 11**.
Allow about **3 GB of free space** during local preview preparation. First startup
prepares local previews and graphics; successful preparation is reused.
Use `Client-einrichten.cmd` to reopen setup.

For updates, keep your existing `reports/native-client.ini` and private identity files.
Do not share private keys or passwords when reporting a problem.

## What is included?

- A community Halo 4 PC client with a server browser and player setup.
- Multiplayer using original maps from each player's local MCC installation.
- Global and team text chat, configurable communication shortcuts and voice microphone/channel/volume settings.
- A dedicated server package with configuration templates, setup tools and Windows/Linux launchers.

## Run your own server (Halo 4 Dedicated Server)

Use the [server ZIP](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/server-v0.2.10-preview/LumenCore-Server-0.2.10-preview.zip)
with the matching **Lumen Core 0.2.10-preview client**. The published pair uses
native compatibility version **0.2.8**.

The server is a Windows x64 program. On Linux x86_64, it runs through **Wine 11**;
there is no separate native Linux executable. Operators supply their own supported
local Steam MCC data. First startup creates new server identities and credentials.

**[Read the German server setup guide](SERVER-ANLEITUNG.md)** for game-data preparation,
Windows/Linux startup, ports, client certificate setup, RCON administration and troubleshooting.
Keep generated `game/` and `data/` folders private. Run the server under a regular
local account, as explained in the guide.

## Frequently asked questions

### Does the download include Halo 4 or MCC?

No. You need your own supported Steam MCC installation with Halo 4. Downloads contain
no MCC engine DLL, game maps, exported Halo models, textures or loading artwork.
Setup reads your local game files and writes previews into the separate client folder.

### Can I run a Halo 4 dedicated server on Linux?

The server package supports the documented Linux/Wine setup. The existing deployment
uses Debian 13 and Wine 11; other distributions were not newly tested for this package.
The player client is a Windows application.

### Is 128-player Halo 4 multiplayer supported?

**No.** An experimental 128-slot session configuration is not proof of working
simultaneous 128-player gameplay. This preview is intended for small-group testing.

### Are custom Elite gameplay and custom emotes available?

They are **paused in the public build**. Local menu preview preparation does not
enable these gameplay features.

### Is this a stable or official Halo release?

No. Builds are unsigned early previews. The 0.2.10 public publication was packaged
and statically checked; no additional gameplay test was run for that publication.
See its release notes for the exact scope. Later local development tests do not
automatically validate an older public download.

## Help, source and notices

Report reproducible problems at [Issues](https://github.com/LumenCore-dev/Lumen-core-Client/issues)
with the version, map, Windows/GPU details, steps and expected versus actual behavior.
Review personal details before sharing logs.

Matching GPL preview-tool source and third-party notices are included with the
[client release](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.10-preview).
The preview tool is unchanged from 0.2.9. Program-owned text and colors are used
for setup and loading screens.

Independent community project, not affiliated with or endorsed by Microsoft or
Halo Studios. Halo and MCC belong to their owners.
