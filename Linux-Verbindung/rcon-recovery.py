"""Enable failure recovery for the existing dedicated service, keeping manual stops."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

root=Path('/opt/halo4')
unit=Path('/etc/systemd/system/halo4-dedicated.service')
if 'Description=Halo 4 Dedicated Server under Wine' not in unit.read_text():
    raise RuntimeError('Unexpected unit; no change made')
folder=Path('/etc/systemd/system/halo4-dedicated.service.d')
folder.mkdir(exist_ok=True)
path=folder/'50-failure-recovery.conf'
text='''[Unit]
StartLimitIntervalSec=120
StartLimitBurst=5

[Service]
Restart=on-failure
RestartSec=5
'''
backup=root/'data/desktop-backups'
backup.mkdir(parents=True,exist_ok=True)
if path.exists() and path.read_text()!=text:
    shutil.copy2(path,backup/('recovery-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'.conf'))
path.write_text(text)
path.chmod(0o644)
subprocess.run(['systemctl','daemon-reload'],check=True)
result=subprocess.run(['systemctl','show','halo4-dedicated.service','--property=Restart,RestartUSec,ActiveState,SubState,MainPID'],capture_output=True,text=True,check=True)
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'recovery_file':str(path),'effective':result.stdout,'password_changed':False,'rcon_exposed':False}))
