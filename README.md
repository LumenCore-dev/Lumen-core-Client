# Lumen Core

A community client for Halo 4 on PC, by **Lumen Core Community**.

**Early preview — small-group testing.** Requires your own Steam copy of
Halo: The Master Chief Collection with Halo 4 installed. This project does
not distribute the MCC engine, maps, or exported game models and textures.

## Download

Get the Windows x64 client from [Releases](https://github.com/LumenCore-dev/Lumen-core-Client/releases).
Use **0.2.9-preview or newer** for the community server. Extract the entire ZIP
into its own writable folder and start **LumenCore.exe**. Keep the included
`server-trust` folder and session/build files; copying only the EXE is insufficient.
Do not run it from inside the ZIP or place it inside your MCC installation.

The first launch guides you through selecting MCC and setting your player name.
Setup uses German on German Windows display languages and English otherwise.
After installing a new version, graphics are prepared automatically in the
loading screen before the client opens. Successful preparation is remembered;
subsequent launches skip it. Use `Client-einrichten.cmd`
only if you want to reopen setup.

Windows 10/11 x64, .NET Framework 4.8 and DirectX 11 graphics are required.
The client checks that the installed Halo 4 engine version is supported.

## Current status

- Client setup and real map loading are under active testing.
- The package connects to the community test server by default.
- **128-player gameplay is not yet supported or verified.** Expanded session
  admission is experimental and does not remove the remaining engine limits.
- Setup creates the Spartan and Elite 3D previews from your own MCC installation.
  Allow a few minutes and 3 GB free during preparation; the finished previews
  use about 705 MB and are reused on later launches. No game assets are bundled.
  Supported saved Spartan armor, colors and visor presets apply on multiplayer
  join. Elite, detail tint and unsupported variants remain preview-only.
- Two real clients were used to check different saved appearances and session
  departure. This is not a 128-player load test.
- Some in-game menus are still German. Builds are currently unsigned.
- Automatic loading preparation warms a real local map; it does not compile
  every shader for all maps and effects.

Keep your existing `reports/native-client.ini` when updating; it contains your
settings. Do not share personal profiles, private keys or unreviewed debug logs.

## Testing and issues

Use [Issues](https://github.com/LumenCore-dev/Lumen-core-Client/issues) for reproducible bugs.
Include the client version, map, Windows/GPU, steps to reproduce, and what you
expected versus what happened. Start with a few players before larger tests.

## About

Independent community project, not affiliated with or endorsed by Microsoft
or Halo Studios. Halo and MCC belong to their respective owners. Third-party
notices are included in the client package.
