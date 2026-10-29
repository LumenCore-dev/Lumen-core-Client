# Lumen Core — Halo 4 MCC Client & Dedicated Server

A custom client and dedicated server implementation for **Halo 4 on PC (MCC)**, enabling LAN and online multiplayer sessions with full server control.

> **Requires a legal copy of Halo: The Master Chief Collection on Steam.**  
> No game assets, map files, or Microsoft/343 Industries intellectual property are distributed here.

---

## Features

- **LumenCore Client** — custom launcher with overlay, admin tools and identity management
- **Dedicated Server** — headless Halo 4 server supporting up to 128 players
- **Custom Game Modes** — Gun Game, Weapon Deathmatch, CTF, Slayer and more
- **RCON Console** — remote administration via the included RCON client
- **Map Voting** — players vote on the next map after each round
- **Bot support** — configurable bot count and difficulty (native adapter in progress)
- **Server Policy** — kick/mute/ban, vote system, word filter, ping limit
- **Custom Maps** — drop your own `.map` files into `custom-maps/`

---

## Requirements

| Component | Minimum |
|-----------|---------|
| OS | Windows 10 / 11 (64-bit) |
| Halo MCC | Installed via Steam (App ID 976730) |
| .NET | .NET 9 Runtime (included in `Client/tools/`) |
| RAM | 4 GB |
| Network | LAN or public IPv4 |

---

## Quick Start

### Client

1. Install Halo: The Master Chief Collection via Steam
2. Run `Client/Client-einrichten.cmd` once to set up paths
3. Start with `Client/Start-Client.cmd`

### Dedicated Server

1. Run `Server/Start-Server.cmd` for a single multiplayer server
2. Run `Server/Start-Lobbys.cmd` for the full lobby stack (master + game servers)
3. Edit `Server/server.cfg` or `Server/dedicated.cfg` to change maps, modes and limits

### Remote Administration

```cmd
Server\RCON-Konsole.cmd
```

Uses Source RCON protocol — any Source RCON client works (default port 49182).

---

## Server Configuration

| File | Purpose |
|------|---------|
| `Server/server.cfg` | Native dedicated server (single process, Gun Game / Deathmatch) |
| `Server/dedicated.cfg` | Lobby stack (master + multiple game servers, up to 128 players) |
| `Server/server-policy.cfg` | Moderation rules, vote settings, conduct policy |
| `Server/deathmatch.cfg` | Weapon Deathmatch preset |
| `Server/gungame.cfg` | Gun Game preset |

---

## Directory Layout

```
Lumen-core-Client/
├── Client/
│   ├── LumenCore.exe           # Custom client launcher
│   ├── LumenCoreRuntime.dll    # Client runtime
│   ├── Halo4NativeClient.exe   # Native game host
│   ├── Halo4LobbyServer.exe    # Lobby process
│   ├── config/                 # Client configuration
│   ├── runtime/                # Diagnostic utilities
│   └── tools/                  # .NET runtime dependencies
└── Server/
    ├── Halo4DedicatedServer.exe     # Dedicated server (standard)
    ├── Halo4DedicatedServer-online.exe  # Online/public variant
    ├── Halo4LobbyServer.exe         # Lobby server
    ├── server.cfg                   # Main server config
    ├── dedicated.cfg                # Multi-server stack config
    └── server-policy.cfg            # Moderation policy
```

---

## Legal

This project is a **custom server implementation** using reverse-engineered memory layouts and public references. It does **not** distribute any Microsoft or 343 Industries assets, binaries, or intellectual property.

Third-party notices (Dear ImGui, MinHook, HaloCheckpointManager, MCCVR-Halo-Build) are listed in [`Client/NOTICES.md`](Client/NOTICES.md).

**Halo**, **Halo: The Master Chief Collection**, and related marks are trademarks of **Microsoft Corporation**.

---

## Contributing

Pull requests and issues are welcome. Please test any server-side changes with at least 2 clients before submitting.
