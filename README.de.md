# Lumen Core — Halo 4 Multiplayer und Dedicated Server für PC

Lumen Core ist ein unabhängiges Community-Projekt für **Halo 4 Multiplayer auf dem PC**:
ein Windows-Client mit Serverbrowser und ein separates Paket für einen **eigenen
Halo-4-Dedicated-Server** unter Windows oder Linux mit Wine. Es ist eine frühe
Preview für Tests in kleinen Gruppen. Du brauchst deine eigene unterstützte
**Steam-Installation von Halo: The Master Chief Collection (MCC)** mit installierter
Halo-4-Kampagne und Multiplayer.

[Windows-Client herunterladen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.10-preview/LumenCore-0.2.10-preview-win64.zip)
· [Eigenen Server einrichten](SERVER-ANLEITUNG.md)
· [English](README.md)
· [Problem melden](https://github.com/LumenCore-dev/Lumen-core-Client/issues)

## Halo 4 Multiplayer spielen

1. Die eigene Steam-MCC-Installation einschließlich Halo-4-Kampagne und Multiplayer installieren.
2. Die vollständige [Client-ZIP 0.2.10-preview](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.10-preview/LumenCore-0.2.10-preview-win64.zip) außerhalb von Steam/MCC in einen beschreibbaren Ordner entpacken.
3. **`LumenCore.exe`** starten, den MCC-Ordner auswählen und das Spielerprofil einrichten.
4. Die erste Vorbereitung abschließen lassen und über den Serverbrowser einen konfigurierten Server öffnen.

Voraussetzungen: **Windows 10/11 x64, .NET Framework 4.8 und DirectX 11**.
Für die lokale Vorschauvorbereitung etwa **3 GB freien Speicher** einplanen.
Erfolgreiche Vorbereitungen werden wiederverwendet. `Client-einrichten.cmd` öffnet
die Einrichtung erneut.

Bei Updates die vorhandene `reports/native-client.ini` und privaten Identitätsdateien
behalten. Private Schlüssel und Passwörter nicht weitergeben.

## Eigenen Halo 4 Dedicated Server hosten

Die [Server-ZIP 0.2.10-preview](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/server-v0.2.10-preview/LumenCore-Server-0.2.10-preview.zip)
enthält eine Konfigurationsvorlage, Einrichtungswerkzeuge und Startskripte. Dazu gehört
der passende Client 0.2.10-preview; die native Kompatibilitätsversion ist **0.2.8**.

Der Server ist ein Windows-x64-Programm. Auf Linux x86_64 läuft dieselbe EXE über
**Wine 11**. Die bestehende Bereitstellung nutzt Debian 13/Wine 11; andere Distributionen
wurden für dieses Paket nicht neu getestet. Eine eigenständige native Linux-Binary
ist nicht enthalten. Der Spieler-Client benötigt Windows.

Die **[deutsche Server-Anleitung](SERVER-ANLEITUNG.md)** beschreibt eigene MCC-Daten,
Windows-/Linux-Start, Ports, vertrauenswürdige Serverzertifikate, RCON und Fehlerbehebung.
Den Server unter einem normalen lokalen Konto starten. Die erzeugten Ordner `game/`
und `data/` bleiben privat.

## Funktionen und Grenzen der Preview

- Multiplayer mit Originalkarten aus der eigenen MCC-Installation.
- Serverbrowser, Spieler-Einrichtung, globaler Chat und Teamchat.
- Einstellbare Kommunikations-Tasten und Sprachchat-Einstellungen für Mikrofon, Kanal und Lautstärke.
- Separates Dedicated-Server-Paket für eigene Server.

**128 gleichzeitig spielende Personen sind nicht unterstützt oder nachgewiesen.**
Die experimentelle 128er-Sitzungskonfiguration ist kein Gameplay-Kapazitätsnachweis.
Angepasstes Elite-Gameplay und angepasste Emotes sind im öffentlichen Build pausiert.
Lokale Menüvorschauen aktivieren diese Spielfunktionen nicht.

Die EXEs sind nicht signierte frühe Previews. Bei der Veröffentlichung von 0.2.10
wurden Paket und Dateien statisch geprüft; für diese Veröffentlichung wurde kein
zusätzlicher Gameplay-Test durchgeführt. Spätere lokale Entwicklungstests sind
keine automatische Freigabe älterer Downloads.

## Ist Halo 4 im Download enthalten?

Nein. Du brauchst eine eigene unterstützte Steam-MCC-Installation. Die Pakete enthalten
keine MCC-Engine-DLLs, Karten oder exportierten Halo-Modelle, Texturen und Ladebilder.
Die Einrichtung liest die eigenen Spieldaten und erzeugt Vorschauen im separaten
Client-Ordner. GPL-Quellcode des Vorschauwerkzeugs und Lizenzhinweise sind beim
[Client-Release](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.10-preview) verfügbar.

## Hilfe und Downloads

- [Client-Release mit Versionshinweisen und Prüfsummen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.10-preview)
- [Server-Release mit Versionshinweisen und Prüfsummen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/server-v0.2.10-preview)
- [Fehler melden](https://github.com/LumenCore-dev/Lumen-core-Client/issues): Version, Karte, Windows/GPU, Schritte und erwartetes/tatsächliches Verhalten angeben. Logs vor dem Teilen auf persönliche Daten prüfen.

Unabhängiges Community-Projekt, weder mit Microsoft noch Halo Studios verbunden
oder von ihnen unterstützt. Halo und MCC gehören ihren jeweiligen Rechteinhabern.
