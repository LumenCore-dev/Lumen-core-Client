"""Read-only diagnostics; never print password or private-key material."""
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import time

root = Path('/opt/halo4')
def command(*args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return {'code':p.returncode,'out':p.stdout[-14000:],'error':p.stderr[-2000:]}
def meta(path):
    path=Path(path)
    if not path.exists():return {'exists':False,'path':str(path)}
    s=path.stat()
    return {'exists':True,'path':str(path),'size':s.st_size,'owner':pwd.getpwuid(s.st_uid).pw_name,'mode':oct(s.st_mode & 0o777),'age_seconds':int(time.time()-s.st_mtime),'service_readable':command('runuser','-u','halo4-dedicated','--','test','-r',str(path))['code']==0}
cfg={}
for line in (root/'server.cfg').read_text().splitlines():
    if '=' in line and not line.strip().startswith(('#',';')):
        k,v=line.split('=',1);cfg[k.strip()]=v.strip()
database=Path(cfg.get('database','data/server.sqlite3'))
password=root/cfg.get('rcon_password_file',str(database.with_suffix('.rcon-password.txt')))
tls=root/cfg.get('tls_identity',str(database.with_suffix('.tls')))
files=[root/'server.cfg',password,tls/'server.der',root/'Halo4DedicatedServer.exe',root/'halo4-engine-host.dll']
report={'ok':True,'config':{k:cfg.get(k) for k in ('bind','rcon_bind','rcon_password_file','tls_identity','database','game_directory','network','master_address')},'files':[meta(p) for p in files]}
if password.exists():
    secret=password.read_text().strip()
    report['password_valid']=16<=len(secret.encode())<=256 and not any(ord(c)<32 for c in secret)
report['service']=command('systemctl','show','halo4-dedicated.service','--property=User,Group,ExecStart,ActiveState,SubState,Result,ExecMainStatus,Environment,DropInPaths')
report['unit']=command('systemctl','cat','halo4-dedicated.service')
report['listeners']=command('ss','-lntup')
report['listeners']['out']='\n'.join(line for line in report['listeners']['out'].splitlines() if any(p in line for p in ('49175','49180','49181','49182')))
report['memory']=command('free','-m')
report['disk']=command('df','-h','/opt/halo4')
path=root/'data/engine/native-server.json'
if path.exists():
    state=json.loads(path.read_text())
    report['native_state']={k:state.get(k) for k in ('status','phase','error','engine_exit_reason','dedicated_audio_disabled','dedicated_audio_backend_initialized','headless_render_mode','map_loaded')}
    report['native_state']['age_seconds']=meta(path)['age_seconds']
report['engine_logs']={}
for name in ('server-core.log','server-console.log'):
    path=root/'data/engine'/name
    if path.exists():report['engine_logs'][name]=path.read_text(errors='replace')[-10000:]
print('HALO4_MAINTENANCE:'+json.dumps(report))
