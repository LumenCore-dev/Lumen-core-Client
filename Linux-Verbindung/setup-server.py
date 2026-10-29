"""Provision only the Halo 4 VPN and service; never print private credentials."""
import os
from pathlib import Path
import pwd
import subprocess
import sys

os.umask(0o077)
def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)

root = Path('/opt/halo4')
if sys.argv[1:] == ['service']:
    if not (root/'SHA256SUMS').is_file():
        raise SystemExit('Upload ist noch nicht vollstaendig.')
    run('sha256sum', '--quiet', '-c', 'SHA256SUMS', cwd=root)
    user = 'halo4-dedicated'
    try:
        account = pwd.getpwnam(user)
        if account.pw_dir != str(root):
            raise SystemExit('Benutzername bereits anderweitig verwendet.')
    except KeyError:
        run('useradd', '--system', '--user-group', '--home-dir', str(root), '--shell', '/usr/sbin/nologin', user)
        account = pwd.getpwnam(user)
    os.chown(root, account.pw_uid, account.pw_gid)
    for item in root.rglob('*'):
        if item.is_symlink():
            raise SystemExit('Unerwartete Verzeichnisverknuepfung im Upload.')
        os.chown(item, account.pw_uid, account.pw_gid)
    unit = Path('/etc/systemd/system/halo4-dedicated.service')
    if unit.exists():
        raise SystemExit('Halo-4-Dienst existiert bereits; kein Ueberschreiben.')
    unit.write_text('''[Unit]
Description=Halo 4 Dedicated Server under Wine
After=network-online.target

[Service]
Type=simple
User=halo4-dedicated
Group=halo4-dedicated
WorkingDirectory=/opt/halo4
Environment=HOME=/opt/halo4
Environment=WINEPREFIX=/opt/halo4/.wine-halo4 WINEARCH=win64 WINEDEBUG=-all
Environment=HALO4_HEADLESS_CPU_GRAPHICS_PROBE=1 HALO4_HEADLESS_NO_D3D_PROBE=1 HALO4_HEADLESS_DYNAMIC_ARENA=1
ExecStart=/usr/bin/xvfb-run -a --server-args="-screen 0 1280x720x24 -nolisten tcp" /usr/bin/wine /opt/halo4/Halo4DedicatedServer.exe --config server.cfg
UMask=0077
KillMode=control-group
TimeoutStopSec=30
Restart=no
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
''')
    run('systemctl', 'daemon-reload')
    run('systemctl', 'start', 'halo4-dedicated.service')
    print('Pruefsummen OK. Serverdienst fuer ersten Start gestartet; Autostart noch aus.')
else:
    raise SystemExit('Usage: setup-server.py service')
