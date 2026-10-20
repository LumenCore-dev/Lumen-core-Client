# Lumen Core â€” Halo 4 Multiplayer und Dedicated Server fÃ¼r PC

Lumen Core ist ein unabhÃ¤ngiges Community-Projekt fÃ¼r **Halo 4 Multiplayer auf dem PC**:
ein Windows-Client mit Serverbrowser und ein separates Paket fÃ¼r einen **eigenen
Halo-4-Dedicated-Server** unter Windows oder Linux mit Wine. Es ist eine frÃ¼he
Preview fÃ¼r Tests in kleinen Gruppen. Du brauchst deine eigene unterstÃ¼tzte
**Steam-Installation von Halo: The Master Chief Collection (MCC)** mit installierter
Halo-4-Kampagne und Multiplayer.

[Windows-Client herunterladen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.11-preview/LumenCore-0.2.11-preview-win64.zip)
Â· [Eigenen Server einrichten](SERVER-ANLEITUNG.md)
Â· [English](README.md)
Â· [Problem melden](https://github.com/LumenCore-dev/Lumen-core-Client/issues)

## Halo 4 Multiplayer spielen

1. Die eigene Steam-MCC-Installation einschlieÃŸlich Halo-4-Kampagne und Multiplayer installieren.
2. Die vollstÃ¤ndige [Client-ZIP 0.2.11-preview](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/v0.2.11-preview/LumenCore-0.2.11-preview-win64.zip) auÃŸerhalb von Steam/MCC in einen beschreibbaren Ordner entpacken.
3. **`LumenCore.exe`** starten, den MCC-Ordner auswÃ¤hlen und das Spielerprofil einrichten.
4. Die erste Vorbereitung abschlieÃŸen lassen und Ã¼ber den Serverbrowser einen konfigurierten Server Ã¶ffnen.

Voraussetzungen: **Windows 10/11 x64, .NET Framework 4.8 und DirectX 11**.
FÃ¼r die lokale Vorschauvorbereitung etwa **3 GB freien Speicher** einplanen.
Erfolgreiche Vorbereitungen werden wiederverwendet. `Client-einrichten.cmd` Ã¶ffnet
die Einrichtung erneut.

Bei Updates die vorhandene `reports/native-client.ini` und privaten IdentitÃ¤tsdateien
behalten. Private SchlÃ¼ssel und PasswÃ¶rter nicht weitergeben.

## Eigenen Halo 4 Dedicated Server hosten

Die [Server-ZIP 0.2.11-preview](https://github.com/LumenCore-dev/Lumen-core-Client/releases/download/server-v0.2.11-preview/LumenCore-Server-0.2.11-preview.zip)
enthÃ¤lt eine Konfigurationsvorlage, Einrichtungswerkzeuge und Startskripte. Dazu gehÃ¶rt
der passende Client 0.2.11-preview; die native KompatibilitÃ¤tsversion ist **0.2.8**.

Der Server ist ein Windows-x64-Programm. Auf Linux x86_64 lÃ¤uft dieselbe EXE Ã¼ber
**Wine 11**. Die bestehende Bereitstellung nutzt Debian 13/Wine 11; andere Distributionen
wurden fÃ¼r dieses Paket nicht neu getestet. Eine eigenstÃ¤ndige native Linux-Binary
ist nicht enthalten. Der Spieler-Client benÃ¶tigt Windows.

Die **[deutsche Server-Anleitung](SERVER-ANLEITUNG.md)** beschreibt eigene MCC-Daten,
Windows-/Linux-Start, Ports, vertrauenswÃ¼rdige Serverzertifikate, RCON und Fehlerbehebung.
Den Server unter einem normalen lokalen Konto starten. Die erzeugten Ordner `game/`
und `data/` bleiben privat.

## Funktionen und Grenzen der Preview

- Multiplayer mit Originalkarten aus der eigenen MCC-Installation.
- Serverbrowser, Spieler-Einrichtung, globaler Chat und Teamchat.
- Einstellbare Kommunikations-Tasten und Sprachchat-Einstellungen fÃ¼r Mikrofon, Kanal und LautstÃ¤rke.
- Separates Dedicated-Server-Paket fÃ¼r eigene Server.

**128 gleichzeitig spielende Personen sind nicht unterstÃ¼tzt oder nachgewiesen.**
Die experimentelle 128er-Sitzungskonfiguration ist kein Gameplay-KapazitÃ¤tsnachweis.
Angepasstes Elite-Gameplay und angepasste Emotes sind im Ã¶ffentlichen Build pausiert.
Lokale MenÃ¼vorschauen aktivieren diese Spielfunktionen nicht.

Die EXEs sind nicht signierte frühe Previews. Dieser Build wurde mit zwei Windows-Clients,
fünf Minuten Laufzeit und Kartenwechsel getestet. Linux/Wine wurde auf Lobby/RCON geprüft;
Linux-Gameplay, ein zweiter PC und hohe Spielerzahlen sind nicht nachgewiesen.

## Ist Halo 4 im Download enthalten?

Nein. Du brauchst eine eigene unterstÃ¼tzte Steam-MCC-Installation. Die Pakete enthalten
keine MCC-Engine-DLLs, Karten oder exportierten Halo-Modelle, Texturen und Ladebilder.
Die Einrichtung liest die eigenen Spieldaten und erzeugt Vorschauen im separaten
Client-Ordner. GPL-Quellcode des Vorschauwerkzeugs und Lizenzhinweise sind beim
[Client-Release](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.11-preview) verfÃ¼gbar.

## Hilfe und Downloads

- [Client-Release mit Versionshinweisen und PrÃ¼fsummen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.11-preview)
- [Server-Release mit Versionshinweisen und PrÃ¼fsummen](https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/server-v0.2.11-preview)
- [Fehler melden](https://github.com/LumenCore-dev/Lumen-core-Client/issues): Version, Karte, Windows/GPU, Schritte und erwartetes/tatsÃ¤chliches Verhalten angeben. Logs vor dem Teilen auf persÃ¶nliche Daten prÃ¼fen.

UnabhÃ¤ngiges Community-Projekt, weder mit Microsoft noch Halo Studios verbunden
oder von ihnen unterstÃ¼tzt. Halo und MCC gehÃ¶ren ihren jeweiligen Rechteinhabern.
