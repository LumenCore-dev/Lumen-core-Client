from pathlib import Path
import json,subprocess,hashlib
root=Path('/opt/halo4');report=json.loads((root/'join-leave-tdm-deployment.json').read_text())
assert subprocess.check_output(['systemctl','is-active','halo4-dedicated'],text=True).strip()=='active'
state=json.loads((root/'data/engine/native-server.json').read_text())
assert state['status']=='DEDICATED_LOBBY_READY' and state['session_bank_wide']
assert hashlib.sha256((root/'Halo4DedicatedServer.exe').read_bytes()).hexdigest()==report['server_sha256']
processes=subprocess.check_output(['ps','-u','halo4-dedicated','-o','comm='],text=True).splitlines()
assert sum(p.strip().startswith('Halo4Dedicated') for p in processes)==1
report['restart_count']=int(subprocess.check_output(['systemctl','show','halo4-dedicated','-p','NRestarts','--value'],text=True).strip())
assert report['restart_count']==0
print('HALO4_MAINTENANCE:'+json.dumps(report))
