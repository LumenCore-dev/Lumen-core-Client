from pathlib import Path
import json
import subprocess
import sys
import time

root=Path('/opt/halo4')
sys.path.insert(0,str(root))
from rcon_client import Client

with Client('127.0.0.1',49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
    answer=client.run('stop')
print('Authenticated stop requested: '+answer.strip(),flush=True)
deadline=time.monotonic()+25
while subprocess.run(['systemctl','is-active','--quiet','halo4-dedicated.service']).returncode==0:
    if time.monotonic()>deadline:
        raise SystemExit('Graceful shutdown timed out.')
    time.sleep(0.25)
exit_code=subprocess.check_output(['systemctl','show','halo4-dedicated.service','--property=ExecMainStatus','--value'],text=True).strip()
if exit_code!='0':
    raise SystemExit('Native process did not shut down cleanly: '+exit_code)
started=time.time()
subprocess.run(['systemctl','start','halo4-dedicated.service'],check=True)
deadline=time.monotonic()+25
while time.monotonic()<deadline:
    path=root/'data/engine/native-server.json'
    state=json.loads(path.read_text())
    if path.stat().st_mtime>=started and state.get('status')=='DEDICATED_LOBBY_READY':
        if state.get('dedicated_audio_disabled') is not True or state.get('dedicated_audio_backend_initialized') is not False:
            raise SystemExit('Audio suppression is not active after restart.')
        break
    time.sleep(0.25)
else:
    raise SystemExit('No fresh ready lobby after restart.')
processes=subprocess.check_output(['ps','-u','halo4-dedicated','-o','comm='],text=True).splitlines()
if 'pulseaudio' in processes:
    raise SystemExit('External audio daemon unexpectedly present.')
result={'status':'GRACEFUL_STOP_AND_RESTART_VERIFIED','native_exit_code':0,'dedicated_audio_disabled':True,'audio_backend_initialized':False,'external_audio_daemon':False,'pulse_audio_packages_removed':not Path('/usr/bin/pulseaudio').exists()}
(root/'restart-no-audio-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
