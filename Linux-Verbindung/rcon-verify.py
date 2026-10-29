"""Authenticate with valid/invalid credentials, inspect TLS and observe a live lobby."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time

root=Path('/opt/halo4')
sys.path.insert(0,str(root))
from rcon_client import Client

cfg={}
for line in (root/'server.cfg').read_text().splitlines():
    if '=' in line and not line.strip().startswith(('#',';')):
        key,value=line.split('=',1);cfg[key.strip()]=value.strip()
secret=(root/cfg['rcon_password_file']).read_text().strip()
cert=root/'data/server.tls/server.der'
results={'ok':True,'checks':{}}
with Client('127.0.0.1',49182,secret,certificate=cert) as client:
    results['tls']=client.stream.version()
    results['alpn']=client.stream.selected_alpn_protocol()
    assert client.stream.getpeercert(binary_form=True)==cert.read_bytes()
    results['checks']['certificate_pin']=True
    for command in ('status','players','help','anticheat status','banlist'):
        result=client.run(command)
        if result.startswith('ERR '):raise RuntimeError(command+': '+result)
        results['checks'][command]=result[:900]
try:
    with Client('127.0.0.1',49182,'invalid-test-password-0000000000',certificate=cert):
        raise RuntimeError('Invalid RCON password was accepted')
except PermissionError:
    results['checks']['wrong_password_rejected']=True
start=time.monotonic()
observations=0
while time.monotonic()-start<40:
    state=subprocess.check_output(['systemctl','is-active','halo4-dedicated.service'],text=True).strip()
    assert state=='active',state
    report=root/'data/engine/native-server.json'
    native=json.loads(report.read_text())
    assert time.time()-report.stat().st_mtime<12,'Stale engine status'
    assert native.get('status') in ('DEDICATED_LOBBY_READY','DEDICATED_WORLD_READY'),native.get('status')
    observations+=1
    time.sleep(4)
results['checks']['stable_observation_seconds']=int(time.monotonic()-start)
results['checks']['fresh_native_observations']=observations
results['native']={key:native.get(key) for key in ('status','phase','dedicated_audio_disabled','dedicated_audio_backend_initialized')}
listeners=subprocess.check_output(['ss','-lntp'],text=True)
results['checks']['rcon_loopback_only']=all('127.0.0.1:49182' in row for row in listeners.splitlines() if ':49182' in row) and '127.0.0.1:49182' in listeners
assert results['checks']['rcon_loopback_only']
print('HALO4_MAINTENANCE:'+json.dumps(results))
