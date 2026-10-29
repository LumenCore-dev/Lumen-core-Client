from pathlib import Path
import json,shutil,subprocess,sys,re
root=Path('/opt/halo4');cfg=(root/'server.cfg').read_text()
selected={}
for line in cfg.splitlines():
 if '=' in line:
  k,v=map(str.strip,line.split('=',1))
  if k in ('map','map_pool','max_players','game_variant','headless'):selected[k]=v
sys.path.insert(0,str(root));from rcon_client import Client
bind=re.search(r'^rcon_bind\s*=\s*(\S+)',cfg,re.M)
host,port=(bind.group(1) if bind else '127.0.0.1:49182').rsplit(':',1)
if host=='0.0.0.0':host='127.0.0.1'
try:
 with Client(host,int(port),(root/'data/rcon-password.txt').read_text().strip(),certificate=root/'data/server.tls/server.der') as c:status=c.run('status').strip()
except Exception as e:status='UNAVAILABLE: '+type(e).__name__
u=shutil.disk_usage(root)
print('HALO4_MAINTENANCE:'+json.dumps({'ok':True,'config':selected,'status':status,'freeBytes':u.free,'emoteDirectoryPresent':(root/'assets/emotes').exists(),'customHugegrassPresent':(root/'game/halo4/maps/hugegrass_port.map').exists()}))
