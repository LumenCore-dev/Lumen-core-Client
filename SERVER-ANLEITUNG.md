# Lumen Core Dedicated Server 0.2.11-preview

Mit diesem Paket betreibst du einen eigenen Halo-4-Server fuer den passenden
Lumen-Core-Client 0.2.11-preview. Native Kompatibilitaet: **0.2.8**.
Der Server ist ein Windows-x64-Programm; Linux nutzt Wine, Xvfb und denselben
integrierten Lobbydienst. Es gibt keine separate native Linux-Binary.

**Im Download sind keine Halo-Spieldaten, Passwoerter, privaten Schluessel,
Spieler-/Ban-Datenbanken oder vorbefuellten Admin-/Moderatorlisten.**
Das Paket verwendet eigene, lokal bereitgestellte Originaldaten aus Steam MCC.
Elite und angepasste Emotes sind deaktiviert. Mit 16 Spielern beginnen;
die interne 128er-Sitzungskonfiguration belegt keinen funktionierenden
Spielbetrieb mit 128 Spielern. Dies ist eine fruehe Preview.

## 1. Was du brauchst

- Eigene vollstaendige Steam-MCC-Installation mit Halo 4. Steam: MCC >
  Verwalten > Lokale Dateien durchsuchen. Gemeint ist der Ordner, der
  `halo4` und `MCC` enthaelt, nicht der Steam-Hauptordner.
- Passender Client: https://github.com/LumenCore-dev/Lumen-core-Client/releases/tag/v0.2.11-preview
- Windows 10/11 x64 oder Linux x86_64 mit einer funktionierenden 64-Bit-Wine-11-
  Installation. Die bestehende Linux-Bereitstellung nutzt Debian 13/Wine 11;
  andere Distributionen wurden fuer dieses Paket nicht neu getestet.
- Python 3.10 oder neuer; nur die Standardbibliothek wird benoetigt.
  Windows: https://www.python.org/downloads/windows/ (Python Launcher `py` mitinstallieren).
- Linux zusaetzlich: Xvfb, xauth und DejaVu-Schriften. Fuer Debian/Ubuntu:
  `sudo apt install python3 xvfb xauth fonts-dejavu-core unzip`
- Wine selbst passend zur Distribution installieren, nicht einfach eine
  beliebige aeltere Version: https://gitlab.winehq.org/wine/wine/-/wikis/Download
  Installation mit `wine --version` pruefen. Bei anderem Wine-Pfad siehe Abschnitt 4.
- Genug Platz fuer die lokalen Daten plus Wine-Prefix und Arbeitskopie der
  Engine. `prepare-game-data.py --plan` zeigt den Datenumfang an.

ZIP in einen eigenen beschreibbaren Ordner ausserhalb von Steam/MCC entpacken.
Weder als Administrator noch als root starten. Spieleordner und Serverordner
getrennt halten. Es werden keine vorhandenen Spielinstallationen gepatcht.

## 2. Eigene Spieldaten vorbereiten (Windows-PC)

PowerShell im entpackten Serverordner oeffnen. Den folgenden Beispielpfad
durch den eigenen MCC-Pfad ersetzen:

```powershell
py -3 prepare-game-data.py "D:\SteamLibrary\steamapps\common\Halo The Master Chief Collection" --plan
py -3 prepare-game-data.py "D:\SteamLibrary\steamapps\common\Halo The Master Chief Collection"
```

Der erste Aufruf zeigt nur Dateianzahl und Groesse. Der zweite kopiert in einen
neuen lokalen `game`-Ordner. Er liest ausschliesslich `halo4/halo4.dll`, die
Halo-4-Asset-Unterordner und `MCC/Binaries/Win64/bink2w64.dll`. Steam-Konten,
`userdata`, andere Spiele und unsere Server-Betriebsdaten gehoeren nicht dazu.
Bekannte Backup-Dateinamen werden ausgelassen. Ein nicht leeres Ziel wird
absichtlich nicht ueberschrieben; fuer eine neue Kopie ein neues Ziel verwenden:
`--destination "D:\MCC-Serverdaten-neu\game"`.

Die Struktur muss anschliessend so aussehen:

```text
lumencore-server/
  Halo4DedicatedServer.exe
  server.cfg.example
  setup-server.py
  start-linux.sh
  Start-Server.cmd
  game/
    halo4/
      halo4.dll
      maps/shared.map
      maps/ca_blood_crash.map
      maps/ca_gore_valley.map
      maps/ca_spiderweb.map
      game_variants/H4_SLAYER_132.bin
      sound/ ... sowie weitere lokal kopierte Halo-4-Assets
    MCC/Binaries/Win64/bink2w64.dll
```

Nur Daten der eigenen Installation fuer den eigenen Server verwenden. Den
entstehenden `game`-Ordner nicht in ein GitHub-Release oder einen oeffentlichen
Download aufnehmen. Das Hilfsskript laedt nichts ins Internet hoch.

Der Server akzeptiert nur diese Engine-SHA-256:
`7c53e7d5bc9848545a1b70e2768242479336fba1b7630d7ab955f7fd0c34fa84`.
Bei abweichender MCC-Version stoppt die Pruefung, bevor die Engine startet.
Die Pruefung nicht umgehen und keine DLL aus unbekannten Downloads ersetzen.

## 3. Dateien auf einen Linux-Server hochladen

1. Mit dem eigenen SSH-Benutzer anmelden und `mkdir -p ~/lumencore-server`
   ausfuehren. Fuer diese Anleitung heisst der Ordner exakt `lumencore-server`.
2. WinSCP oeffnen, Protokoll **SFTP**, Host/IP und deinen SSH-Benutzer angeben.
   Den SSH-Hostschluessel mit den Angaben deines Hosters vergleichen.
3. Rechts nach `/home/DEIN_BENUTZER/lumencore-server` wechseln.
   Links den entpackten Paketordner oeffnen und dessen **Inhalt** uebertragen.
4. Den auf dem eigenen PC vorbereiteten kompletten `game`-Ordner ebenfalls
   dorthin uebertragen. Grosse binaere Dateien vollstaendig uebertragen;
   nach Abbruechen WinSCP fortsetzen lassen und den Abschluss abwarten.
5. Kontrolle: Auf Linux muessen `~/lumencore-server/Halo4DedicatedServer.exe`
   und `~/lumencore-server/game/halo4/halo4.dll` vorhanden sein. Ein zusaetzlicher
   verschachtelter `game/game`-Ordner ist falsch.

WinSCP-Anleitung: https://winscp.net/eng/docs/guide_upload

Alternativ geht OpenSSH/SCP. Im folgenden Beispiel `DEIN_SSH_BENUTZER` und
`SERVER_IP` ersetzen; zuerst den Zielordner auf Linux anlegen:

```powershell
scp .\LumenCore-Server-0.2.11-preview.zip DEIN_SSH_BENUTZER@SERVER_IP:~/lumencore-server/
scp -r .\game DEIN_SSH_BENUTZER@SERVER_IP:~/lumencore-server/
```

Auf Linux das ZIP im Ziel entpacken. Es enthaelt seine Dateien direkt, ohne
zusaetzlichen Paket-Unterordner:

```bash
cd ~/lumencore-server
unzip LumenCore-Server-0.2.11-preview.zip
sha256sum -c FILES.sha256
```

`FILES.sha256` prueft nur mitgelieferte Programm-/Vorlagendateien. Es enthaelt
keine Liste deiner lokalen Spieldaten. Dateien nach der Pruefung konfigurieren.

## 4. Server konfigurieren und starten

**IPv4:** Auf Linux `ip -4 addr` ansehen; auf Windows `ipconfig`. Bei einem
VPS die tatsaechlich am Interface konfigurierte IPv4 nehmen. Hinter einem
Heimrouter die lokale LAN-IP nehmen und Ports am Router weiterleiten.
Keine fremde IP und nicht `0.0.0.0` eintragen. Die Beispiele verwenden
`192.168.1.50`; diese Adresse durch deine eigene ersetzen.

Linux:

```bash
cd ~/lumencore-server
python3 setup-server.py --bind 192.168.1.50 --name "Mein Halo Server"
python3 setup-server.py --check
bash start-linux.sh
```

Falls Wine nicht als `wine` im Suchpfad liegt, den eigenen absoluten Pfad setzen:

```bash
WINE_BIN=/opt/wine-stable/lib/wine/x86_64-unix/wine bash start-linux.sh
```

Windows, PowerShell im Paketordner:

```powershell
py -3 setup-server.py --bind 192.168.1.50 --name "Mein Halo Server"
py -3 setup-server.py --check
.\Start-Server.cmd
```

Windows darf statt einer Datenkopie die vorhandene Installation direkt nutzen:
beim Erstellen der Konfiguration zusaetzlich
`--game-directory "D:\SteamLibrary\steamapps\common\Halo The Master Chief Collection"`
angeben. Linux/Wine verwendet in dieser Anleitung den relativen Ordner `game`;
keinen Windows-Laufwerkspfad vom eigenen PC eintragen.

`setup-server.py` erstellt die Datei **nur, wenn server.cfg noch nicht existiert**.
Spaetere Aenderungen direkt in `server.cfg` vornehmen. Keine Anfuehrungszeichen
um CFG-Werte setzen und jeden Schluessel nur einmal verwenden.

| Einstellung | Bedeutung |
| --- | --- |
| `name` | Eigener Servername, maximal 32 Zeichen |
| `bind` | Lokale IPv4 und Lobbyport, Standard `:49180` |
| `password` | Leer = offener Beitritt; eigener Wert = Beitritt mit Passwort, hoechstens 64 UTF-8-Bytes |
| `map` | Erste Karte; Standard `ca_blood_crash` (Exile) |
| `map_pool` | Kommagetrennte Kartennamen; Standard Exile, Vortex, Daybreak |
| `game_variant` | Z.B. `slayer`, `ctf`, `koth`, `oddball`, `swat`, `ffa`, `gungame` |
| `max_players` | Standard 16; hoehere Werte sind experimentell |
| `min_players` | Mindestanzahl, Standard 1 |
| `round_seconds` | Rundendauer in Sekunden, Standard 600 |
| `map_change` | `vote` fuer Abstimmung oder `rotation` fuer Kartenrotation |
| `vote_seconds` | Abstimmungszeit, 5 bis 120 Sekunden |
| `admins`, `moderators` | Anfangs leer; eigene oeffentliche Spieler-Fingerprints, kommagetrennt |
| `rcon_bind` | Administration standardmaessig nur `127.0.0.1:49182` |
| `rcon_password_file` | Pfad fuer das beim ersten Start neu erzeugte RCON-Passwort |
| `headless` | Fuer diesen Startablauf `true` lassen |

Jede in `map`/`map_pool` verwendete Karte muss lokal vorliegen. Beispiel Haven:
`wraparound`; die Vorlage nutzt Exile `ca_blood_crash`, Vortex `ca_gore_valley`
und Daybreak `ca_spiderweb`. Fuer den Anfang die Vorlage beibehalten.

Der Server ist ohne Mastereintrag per Direktverbindung erreichbar. Fuer eine
Anmeldung am bestehenden Lumen-Core-Verzeichnis optional diesen zusaetzlichen
Eintrag in `server.cfg` setzen:

```ini
master_address = 5.199.139.145:49175
```

Das ist eine oeffentliche Dienstadresse, kein Passwort. Die Anmeldung benoetigt
ausgehendes TCP zu Port 49175 und Erreichbarkeit des eigenen Servers. Ein
Verzeichniseintrag ersetzt weder Portfreigaben noch das Zertifikat fuer Spieler.

## 5. Ports und Firewall

| Port bei der Vorlage | Richtung | Zweck |
| --- | --- | --- |
| TCP 49180 | Eingehend | TLS-Lobby/Beitritt |
| UDP 49180 | Eingehend | Serversuche und Voice |
| UDP 49181 | Eingehend | Nativer Spieltransport |
| TCP 49182 | Nur lokal | RCON; nicht im Router/Provider oeffnen |
| TCP 49175 | Ausgehend, optional | Anmeldung am Masterverzeichnis |

Die drei Spielregeln in Provider-Firewall und Betriebssystem-Firewall setzen.
Hinter einem Router TCP/UDP 49180 und UDP 49181 auf die konfigurierte LAN-IP
weiterleiten. Bei CGNAT ist eine eigene Portweiterleitung haeufig nicht moeglich;
dann eine erreichbare IPv4/VPS-Verbindung beim Anbieter einrichten.
SSH-Zugang fuer Administration erhalten. Fuer dieses Paket IPv4 verwenden.

Falls UFW bereits deine Linux-Firewall verwaltet, lauten die Spielregeln:

```bash
sudo ufw allow 49180/tcp
sudo ufw allow 49180/udp
sudo ufw allow 49181/udp
```

Diese Anleitung aktiviert/ersetzt keine Firewall. Windows zeigt ggf. beim Start
eine Freigabe an; die entsprechenden drei eingehenden Regeln auch dort anlegen.
Bei geaendertem Lobbyport folgt der Spielport als Lobbyport + 1. RCON bleibt
bei seinem ausdruecklich konfigurierten Wert; Regeln und Clientadresse anpassen.

## 6. Spieler verbinden: oeffentliches Zertifikat weitergeben

Beim ersten Start werden neue private Serverdaten automatisch in `data/`
erzeugt. Das Paket enthaelt **keine** vorbereiteten Identitaeten.

1. `data/server.tls/server.der` vom eigenen Server herunterladen.
   **Nur diese oeffentliche Zertifikatsdatei** fuer Spieler freigeben.
2. Im Client neben `LumenCore.exe` den Ordner `server-trust` verwenden.
3. Die Datei nach der vom Spieler verwendeten Adresse benennen. Beispiel:
   `server-trust/203.0.113.10_49180.der`. `203.0.113.10` ist hier eine reine
   Beispieladresse; die echte oeffentliche Server-IP einsetzen. Bei Verbindung
   ueber eine andere Adresse braucht der Client deren passenden Dateinamen.
4. Im Client per Direktverbindung dieselbe IP mit Port `49180` eintragen.
   Das Zertifikat ueber einen vertrauenswuerdigen Kanal beziehen; den im
   Serverlog ausgegebenen SHA-256-Fingerprint bei Bedarf abgleichen.

**Nicht weitergeben:** `identity.bin`, `data/rcon-password.txt`,
`data/*.admin-token.txt`, Datenbanken, Wine-Prefix oder den gesamten `data`-Ordner.
Private TLS-Identitaeten unter Wine/Windows koennen an Benutzer/Praefix gebunden
sein; niemals von unserem Betriebssystem oder einem fremden Server uebernehmen.
Beim normalen Neustart `data/` behalten, damit das vertraute Zertifikat gleich bleibt.

## 7. Administration und ordentliches Stoppen

RCON ist lokal und mit TLS abgesichert. Beispiel direkt auf Linux:

```bash
python3 rcon_client.py --host 127.0.0.1 --port 49182 --certificate data/server.tls/server.der --password-file data/rcon-password.txt status
python3 rcon_client.py --host 127.0.0.1 --port 49182 --certificate data/server.tls/server.der --password-file data/rcon-password.txt players
python3 rcon_client.py --host 127.0.0.1 --port 49182 --certificate data/server.tls/server.der --password-file data/rcon-password.txt stop
```

Unter Windows `python3` durch `py -3` ersetzen. Ohne abschliessenden Befehl
oeffnet das Werkzeug eine interaktive Konsole; `help` zeigt die Befehle.
Eine sichtbare Serverkonsole unter Windows akzeptiert ebenfalls `help`,
`status`, `players`, `next` und `stop`. Fuer einen geregelten manuellen Stopp
RCON `stop` verwenden und warten, bis der Prozess beendet ist.

Vom eigenen PC ueber SSH tunneln, statt RCON oeffentlich zu oeffnen:

```bash
ssh -N -L 49182:127.0.0.1:49182 DEIN_SSH_BENUTZER@SERVER_IP
```

In einem zweiten Terminal `rcon_client.py` mit `--host 127.0.0.1 --port 49182`
und deiner vertrauenswuerdigen oeffentlichen `server.der` verwenden. Ohne
`--password-file` fragt das Werkzeug verdeckt nach dem RCON-Passwort.

Fuer Ingame-Adminrechte im Client unter Profil/Anpassen **Spieler-ID kopieren**
waehlen. Nur den eigenen oeffentlichen 64-stelligen Fingerprint in `admins =`
eintragen; weitere Fingerprints mit Komma trennen. Server danach neu starten.
Niemals private Client-Schluessel oder Profilordner uebertragen. Die Vorlage
enthaelt keine Betreiber-/Spieler-IDs und keine vorbereiteten Banlisten.

## 8. Optional: Linux-Autostart fuer deinen SSH-Benutzer

Erst den manuellen Start einrichten. Paket liegt unter `~/lumencore-server`.
Die Beispiel-Unit ist ein **Benutzerdienst**, kein root-Systemdienst.
Bei abweichendem Wine-Pfad vorher `Environment=WINE_BIN=...` in der Vorlage
anpassen. Vor dem Start des Dienstes eine laufende manuelle Instanz mit RCON stoppen.

```bash
mkdir -p ~/.config/systemd/user
cp lumencore-server.service.example ~/.config/systemd/user/lumencore-server.service
systemctl --user daemon-reload
systemctl --user enable --now lumencore-server.service
systemctl --user status lumencore-server.service
journalctl --user -u lumencore-server.service -n 50
```

Soll der Dienst auch nach dem SSH-Logout und nach dem Booten laufen:
`sudo loginctl enable-linger "$USER"`. Stoppen:
`systemctl --user stop lumencore-server.service`; Autostart entfernen:
`systemctl --user disable lumencore-server.service`.
Dieser Dienst startet nach einem Absturz erneut. `systemctl --user stop` beendet
die Dienstgruppe; vor Wartung nach Moeglichkeit zuerst per RCON geordnet stoppen.

## 9. Updates, Backups und Fehler

- Server geordnet stoppen. `server.cfg`, `data/` und den Wine-Prefix privat
  sichern. Keine Backups in oeffentliche Downloads/Git-Repositories legen.
- Neue Version in einen frischen Ordner entpacken und Pruefsummen kontrollieren.
  Eigene Konfiguration nicht durch die Beispielkonfiguration ersetzen.
  Private Identitaeten und Wine-Prefix auf demselben System/Benutzer erhalten.
- Passende Client-/Server-Kompatibilitaet verwenden. Dieses Paket verwendet
  native Kompatibilitaet 0.2.8 mit neu gebauten und getesteten Programmen.
- Keine angepassten Elite-/Emote-Caches hochladen; sie werden nicht verwendet.
- `setup-server.py --check` meldet fehlende Karten/Engineversionen, startet aber
  keine Sitzung und ersetzt keinen Beitrittstest.
- Diagnose: `data/engine/native-server.json`, `data/engine/server-core.log`
  und ggf. das systemd-Journal. Logs vor Weitergabe auf Spieler-/Netzdaten pruefen.
- `DEDICATED_LOBBY_READY` belegt die native Lobby-Bereitschaft. Erfolgreicher
  Beitritt, Kartenstart und Spielbewegung muessen im eigenen Betrieb beobachtet
  werden. Dieser Build wurde mit zwei Windows-Clients, fuenf Minuten Laufzeit und Kartenwechsel getestet. Linux/Wine wurde auf Lobby/RCON geprueft; Linux-Gameplay ist nicht nachgewiesen.
- Fehlendes Zertifikat: Abschnitt 6. Falsche Datenversion: Engine-SHA pruefen.
  Nicht erreichbar: lokale Bind-IP, Provider-/OS-Firewall, Router und Zertifikat
  pruefen. Port belegt: alte Instanz stoppen; nicht zwei Instanzen im selben Ordner starten.

Fehler melden: https://github.com/LumenCore-dev/Lumen-core-Client/issues
Version, Betriebssystem, Wine-Version und nachvollziehbare Schritte angeben.
Passwoerter, private Identitaeten und volle Datenbanken nicht anhaengen.

Unabhaengiges Communityprojekt; keine Verbindung zu Microsoft/Halo Studios.
Halo und MCC gehoeren ihren jeweiligen Rechteinhabern. Enthaltene
Programmbibliotheken: siehe `NOTICES.md`, `licenses/` und `THIRD-PARTY-LICENSES.md`.
