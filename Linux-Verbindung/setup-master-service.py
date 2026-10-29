from pathlib import Path
import json
import socket
import subprocess
import time

root = Path('/opt/halo4')
unit = Path('/etc/systemd/system/halo4-master.service')
description = 'Description=Halo 4 Master Directory under Wine'
if unit.exists() and description not in unit.read_text():
    raise SystemExit('Unexpected existing master service; leaving it unchanged.')
if not (root/'Halo4LobbyServer.exe').is_file():
    raise SystemExit('Master executable missing.')
def pid():
    return subprocess.check_output(['systemctl','show','halo4-dedicated','-p','MainPID','--value'],text=True).strip()
original_pid = pid()
unit.write_text('''[Unit]
Description=Halo 4 Master Directory under Wine
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
User=halo4-dedicated
Group=halo4-dedicated
WorkingDirectory=/opt/halo4
Environment=HOME=/opt/halo4
Environment=WINEPREFIX=/opt/halo4/.wine-halo4-master-11 WINEARCH=win64 WINEDEBUG=-all
Environment="WINEDLLOVERRIDES=mscoree,mshtml="
ExecStart=/usr/bin/xvfb-run -a --server-args="-screen 0 1280x720x24 -nolisten tcp" /opt/wine-stable/lib/wine/x86_64-unix/wine /opt/halo4/Halo4LobbyServer.exe --master-bind 127.0.0.1:49175 --database data/master.sqlite3
UMask=0077
KillMode=control-group
TimeoutStopSec=30
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
''')
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','start','halo4-master'],check=True)
engine='7c53e7d5bc9848545a1b70e2768242479336fba1b7630d7ab955f7fd0c34fa84'
def health():
    deadline=time.monotonic()+55
    while time.monotonic()<deadline:
        try:
            with socket.create_connection(('127.0.0.1',49175),timeout=2) as connection:
                connection.sendall(f'H4LIST 1 {engine}\n'.encode())
                response=connection.recv(4096).decode().strip()
                if response.startswith(f'H4SERVERS 1 {engine} '):
                    return response
        except OSError:
            pass
        time.sleep(1)
    raise SystemExit('No valid directory response before deadline.')
first=health()
subprocess.run(['systemctl','restart','halo4-master'],check=True)
second=health()
if pid()!=original_pid or original_pid=='0':
    raise SystemExit('Dedicated service PID changed unexpectedly.')
state=json.loads((root/'data/engine/native-server.json').read_text())
if state.get('status')!='DEDICATED_LOBBY_READY':
    raise SystemExit('Dedicated server is not lobby-ready.')
result={'status':'MASTER_START_AND_RESTART_VERIFIED','response':second,'dedicated_pid_unchanged':True,'dedicated_status':state['status'],'master_bind':'127.0.0.1:49175','autostart':{name:subprocess.run(['systemctl','is-enabled',name],capture_output=True,text=True).stdout.strip() for name in ('halo4-master','halo4-dedicated')}}
(root/'master-service-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
