"""Observe a fresh native lobby and test the authenticated operator channel."""
from pathlib import Path
import json
import subprocess
import sys
import time

root = Path('/opt/halo4')
sys.path.insert(0,str(root))
from rcon_client import Client

def ready(state):
    native = state.get('session_diagnostics',{})
    return (state.get('status')=='DEDICATED_LOBBY_READY'
            and state.get('session_snapshot_verified') is True
            and state.get('native_session_descriptor',{}).get('valid') is True
            and state.get('native_peer_membership',{}).get('count',0)>=1
            and native.get('local_owner')==native.get('membership_owner')
            and state.get('native_invite_published') is True
            and state.get('engine_exit_reason',-1)==-1
            and state.get('player_snapshot',{}).get('valid') is False)

start = time.monotonic()
checks = 0
no_audio = '--no-audio' in sys.argv
while time.monotonic()-start < 55:
    subprocess.run(['systemctl','is-active','--quiet','halo4-dedicated.service'],check=True)
    report = root/'data/engine/native-server.json'
    state = json.loads(report.read_text())
    if not ready(state) or time.time()-report.stat().st_mtime > 10:
        raise SystemExit('Native lobby is not fresh and ready: '+state.get('status','unknown'))
    if no_audio:
        if state.get('dedicated_audio_disabled') is not True or state.get('dedicated_audio_backend_initialized') is not False:
            raise SystemExit('Dedicated audio suppression is not active.')
        processes = subprocess.check_output(['ps','-u','halo4-dedicated','-o','comm='],text=True).splitlines()
        if 'pulseaudio' in processes:
            raise SystemExit('Unexpected external audio daemon is running.')
    checks += 1
    if checks%20==1:
        print(f'Native lobby ready, observed {int(time.monotonic()-start)}s.',flush=True)
    time.sleep(1)
with Client('127.0.0.1',49182,(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as client:
    status = client.run('status')
result = {'status':'VERIFIED_NATIVE_LOBBY','observation_seconds':int(time.monotonic()-start),'fresh_lobby_checks':checks,'rcon_status':status,'world_or_client_join_tested':False,'public_gameplay_tested':False}
result['dedicated_audio_disabled_without_daemon'] = no_audio
(root/('startup-no-audio-validation.json' if no_audio else 'startup-validation.json')).write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
