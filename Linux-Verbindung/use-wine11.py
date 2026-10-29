from pathlib import Path
import subprocess

unit = Path('/etc/systemd/system/halo4-dedicated.service')
text = unit.read_text()
if 'Description=Halo 4 Dedicated Server under Wine' not in text:
    raise SystemExit('Unerwarteter Dienst; keine Aenderung.')
wine = Path('/opt/wine-stable/lib/wine/x86_64-unix/wine')
if not wine.is_file():
    raise SystemExit('WineHQ-Runtime noch nicht vollstaendig installiert.')
subprocess.run([str(wine),'--version'],check=True)
text = text.replace('/usr/bin/wine /opt/halo4/Halo4DedicatedServer.exe', str(wine)+' /opt/halo4/Halo4DedicatedServer.exe')
text = text.replace('/opt/wine-stable/bin/wine /opt/halo4/Halo4DedicatedServer.exe', str(wine)+' /opt/halo4/Halo4DedicatedServer.exe')
text = text.replace('WINEPREFIX=/opt/halo4/.wine-halo4 ', 'WINEPREFIX=/opt/halo4/.wine-halo4-11 ')
text = text.replace(' HALO4_HEADLESS_DYNAMIC_ARENA=1', '').replace(' HALO4_HEADLESS_DYNAMIC_ARENA=0', '')
if 'WINEDLLOVERRIDES=' not in text:
    text = text.replace('ExecStart=', 'Environment="WINEDLLOVERRIDES=mscoree,mshtml="\nExecStart=')
unit.write_text(text)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','restart','halo4-dedicated.service'],check=True)
print('Serverstart mit Wine 11 angefordert.')
