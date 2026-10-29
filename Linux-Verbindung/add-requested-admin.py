from pathlib import Path
import json,re,shutil,subprocess,sys,time
root=Path('/opt/halo4');sys.path.insert(0,str(root))
from rcon_client import Client
fingerprint='a98c9a9ed9588438717a022dfe0cff4afa8d7f0c74e86a5bb86af6fa4875c97c'
cfg=root/'server.cfg';original=cfg.read_text();values={}
for line in original.splitlines():
 if '=' in line and not line.strip().startswith(('#',';')):
  k,v=line.split('=',1);values[k.strip()]=v.strip()
host,port=values.get('rcon_bind','127.0.0.1:49182').rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
def command(text):
 with Client(host,int(port),(root/values['rcon_password_file']).read_text().strip(),certificate=root/'data/server.tls/server.der') as c:return c.run(text).strip()
assert command('players')=='PLAYERS 0','Players joined; restart deferred'
admins=[x.strip().lower() for x in values.get('admins','').split(',') if x.strip()]
if fingerprint not in admins:admins.append(fingerprint)
updated,n=re.subn(r'^admins\s*=.*$','admins = '+','.join(admins),original,flags=re.M)
assert n<=1
if not n:updated+='\nadmins = '+','.join(admins)+'\n'
backup=root/'data/desktop-backups'/('before-admin-'+str(time.time_ns())+'.cfg');backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(cfg,backup)
oldpid=subprocess.check_output(['systemctl','show','halo4-dedicated','-p','MainPID','--value'],text=True).strip()
try:
 cfg.write_text(updated)
 subprocess.run(['systemctl','restart','halo4-dedicated.service'],check=True,capture_output=True,timeout=45)
 deadline=time.monotonic()+75;status=''
 while time.monotonic()<deadline:
  try:
   status=command('status')
   if status.startswith('SERVER ') and 'native=true' in status:break
  except (OSError,ValueError):pass
  time.sleep(1)
 else:raise RuntimeError('Server did not become ready')
 newpid=subprocess.check_output(['systemctl','show','halo4-dedicated','-p','MainPID','--value'],text=True).strip()
 assert newpid!='0' and newpid!=oldpid
 assert fingerprint in re.search(r'^admins\s*=\s*(.*)$',cfg.read_text(),re.M).group(1).split(',')
 print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'admin_fingerprint':fingerprint,'persisted':True,'server_restarted':True,'status':status}))
except Exception:
 shutil.copy2(backup,cfg)
 subprocess.run(['systemctl','restart','halo4-dedicated.service'],capture_output=True,timeout=45)
 raise
