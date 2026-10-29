from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time,sqlite3
root=Path('/opt/halo4');sys.path.insert(0,str(root))
from rcon_client import Client
candidate=root/'Halo4DedicatedServer.exe.visitor-counter-v1';exe=root/'Halo4DedicatedServer.exe'
expected='8f1ebd4e38c50296e18b96d4a3295c70b1b06138fdc2be9502524b905f017fe5'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected
values={}
for line in (root/'server.cfg').read_text().splitlines():
 if '=' in line and not line.strip().startswith(('#',';')):
  k,v=line.split('=',1);values[k.strip()]=v.strip()
host,port=values['rcon_bind'].rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
def command(text):
 with Client(host,int(port),(root/values['rcon_password_file']).read_text().strip(),certificate=root/'data/server.tls/server.der') as c:return c.run(text).strip()
assert command('players')=='PLAYERS 0','Players connected; deployment deferred'
backup=root/('rollback-visitor-counter-'+str(time.time_ns()));backup.mkdir(mode=0o700)
shutil.copy2(exe,backup/exe.name);shutil.copy2(root/'server.cfg',backup/'server.cfg')
try:
 subprocess.run(['systemctl','stop','halo4-dedicated.service'],check=True,capture_output=True,timeout=45)
 database=root/values['database']
 with sqlite3.connect(database) as source,sqlite3.connect(backup/'server.sqlite3') as target:source.backup(target)
 shutil.copy2(candidate,exe);subprocess.run(['chown','halo4-dedicated:halo4-dedicated',str(exe)],check=True)
 subprocess.run(['systemctl','start','halo4-dedicated.service'],check=True,capture_output=True,timeout=45)
 deadline=time.monotonic()+75
 while time.monotonic()<deadline:
  try:
   status=command('status');count=command('count')
   if status.startswith('SERVER ') and count.startswith('Besucher: '):break
  except (OSError,ValueError):pass
  time.sleep(1)
 else:raise RuntimeError('Counter server did not become ready')
 assert (root/'server.cfg').read_bytes()==(backup/'server.cfg').read_bytes(),'Configuration changed'
 result={'ok':True,'server_sha256':expected,'status':status,'count':count,'admin_configuration_preserved':True,'backup':str(backup)}
 (root/'visitor-counter-deployment.json').write_text(json.dumps(result,indent=2))
 print('HALO4_MAINTENANCE:'+json.dumps(result))
except Exception:
 subprocess.run(['systemctl','stop','halo4-dedicated.service'],capture_output=True,timeout=45)
 shutil.copy2(backup/exe.name,exe)
 subprocess.run(['chown','halo4-dedicated:halo4-dedicated',str(exe)],check=True)
 subprocess.run(['systemctl','start','halo4-dedicated.service'],capture_output=True,timeout=45)
 raise
