from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time
root=Path('/opt/halo4')
candidate=root/'Halo4DedicatedServer.gungame-ui-candidate.exe'
if not candidate.is_file() or 'name = Halo 4 - Gun Game' not in (root/'server.cfg').read_text():
    raise SystemExit('Candidate or expected Gun Game configuration missing.')
print('Candidate SHA256: '+hashlib.sha256(candidate.read_bytes()).hexdigest(),flush=True)
sys.path.insert(0,str(root))
from rcon_client import Client
with Client('127.0.0.1',49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
    print(client.run('status'),flush=True)
    print(client.run('stop'),flush=True)
end=time.monotonic()+30
while subprocess.run(['systemctl','is-active','--quiet','halo4-dedicated']).returncode==0:
    if time.monotonic()>end:raise SystemExit('Graceful stop timed out.')
    time.sleep(.5)
backup=root/'Halo4DedicatedServer.exe.before-gungame-loadouts'
if not backup.exists():shutil.copy2(root/'Halo4DedicatedServer.exe',backup)
shutil.copy2(candidate,root/'Halo4DedicatedServer.exe')
subprocess.run(['chown','halo4-dedicated:halo4-dedicated',str(root/'Halo4DedicatedServer.exe')],check=True)
start=time.time();subprocess.run(['systemctl','start','halo4-dedicated'],check=True)
end=time.monotonic()+40
while time.monotonic()<end:
    path=root/'data/engine/native-server.json'
    try:
        state=json.loads(path.read_text())
        if path.stat().st_mtime>=start and state.get('status')=='DEDICATED_LOBBY_READY':break
    except (ValueError,OSError):pass
    time.sleep(.5)
else:raise SystemExit('New dedicated server did not become ready.')
print('Gun Game server ready on public IPv4; native loadout validation passed.',flush=True)
