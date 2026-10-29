from pathlib import Path
import json,sys
root=Path('/opt/halo4');sys.path.insert(0,str(root))
from rcon_client import Client
values={}
for line in (root/'server.cfg').read_text().splitlines():
 if '=' in line and not line.strip().startswith(('#',';')):
  k,v=line.split('=',1);values[k.strip()]=v.strip()
host,port=values.get('rcon_bind','127.0.0.1:49182').rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
with Client(host,int(port),(root/values['rcon_password_file']).read_text().strip(),certificate=root/'data/server.tls/server.der') as c:
 result={'status':c.run('status').strip(),'players':c.run('players').strip(),'admins':values.get('admins',''),'moderators':values.get('moderators',''),'policy':values.get('policy','')}
print('HALO4_MAINTENANCE:'+json.dumps(result))
